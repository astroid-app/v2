import threading
import time
import asyncio
from astroidapi import surrealdb_handler, sending_handler
import logging
import json
import os


class QueueProcessor:   

    @classmethod
    async def clearLoadedMessage(cls, endpoint, message):
        print(f"Clearing message for endpoint {endpoint}")
        waiting_secs = 0
        max_secs = 10
        while True:
            check_json = await surrealdb_handler.get_endpoint(endpoint, __file__)
            if (check_json["meta"]["read"]["discord"] == True
                    and check_json["meta"]["read"]["guilded"] == True
                    and check_json["meta"]["read"]["revolt"] == True
                    and check_json["meta"]["read"]["nerimity"] == True):
                check_json["meta"]["message"]["content"] = None
                check_json["meta"]["message"]["attachments"].clear()
                check_json["meta"]["message"]["author"]["avatar"] = None
                check_json["meta"]["message"]["author"]["name"] = None
                check_json["meta"]["message"]["author"]["id"] = None
                check_json["meta"]["trigger"] = False
                check_json["meta"]["sender"] = None
                check_json["meta"]["sender-channel"] = None
                try:
                    check_json["meta"]["message"]["isReply"] = False
                    check_json["meta"]["message"]["reply"]["message"] = None
                    check_json["meta"]["message"]["reply"]["author"] = None
                except:
                    await health_check.HealthCheck.EndpointCheck.repair_structure(endpoint)
                check_json["meta"]["message"]["isReply"] = False
                check_json["meta"]["message"]["reply"]["message"] = None
                check_json["meta"]["message"]["reply"]["author"] = None
                check_json["meta"]["read"]["discord"] = False
                check_json["meta"]["read"]["guilded"] = False
                check_json["meta"]["read"]["revolt"] = False
                check_json["meta"]["read"]["nerimity"] = False
                await surrealdb_handler.update(endpoint, check_json)
                print("Everything is read. Cleared.")
                break

            await asyncio.sleep(1)
            waiting_secs += 1
            if waiting_secs >= max_secs:
                check_json["meta"]["message"]["content"] = None
                check_json["meta"]["message"]["attachments"].clear()
                check_json["meta"]["message"]["author"]["avatar"] = None
                check_json["meta"]["message"]["author"]["name"] = None
                check_json["meta"]["message"]["author"]["id"] = None
                check_json["meta"]["trigger"] = False
                check_json["meta"]["sender"] = None
                check_json["meta"]["sender-channel"] = None
                try:
                    check_json["meta"]["message"]["isReply"] = False
                    check_json["meta"]["message"]["reply"]["message"] = None
                    check_json["meta"]["message"]["reply"]["author"] = None
                except:
                    await health_check.HealthCheck.EndpointCheck.repair_structure(endpoint)
                check_json["meta"]["message"]["isReply"] = False
                check_json["meta"]["message"]["reply"]["message"] = None
                check_json["meta"]["message"]["reply"]["author"] = None
                check_json["meta"]["read"]["discord"] = False
                check_json["meta"]["read"]["guilded"] = False
                check_json["meta"]["read"]["revolt"] = False
                check_json["meta"]["read"]["nerimity"] = False
                await surrealdb_handler.update(endpoint, check_json)
                print("Not everything is read. Cleared anyways.")
                break
    

    @classmethod
    async def appendMessage(cls, endpoint, updated_json):
        is_suspend = await surrealdb_handler.Suspension.get_suspend_status(endpoint)
        if is_suspend["suspended"]:
            print(f"Endpoint {endpoint} is suspended. Not appending message.")
            return False
        print(f"Appending message for endpoint {endpoint}")
        if updated_json is None:
            raise Exception("You must provide a valid 'updated_json' json object to appendMessage.")
        message = updated_json["meta"]["message"]
        message_sender = updated_json["meta"]["sender"]
        message_sender_channel = updated_json["meta"]["sender-channel"]
        message["sender"] = message_sender
        message["sender-channel"] = message_sender_channel
        await surrealdb_handler.QueueHandler.append_to_queue(endpoint, message)
        return True
    
    @classmethod
    async def sendMessage(cls, endpoint):
        try:
            print(f"Sending message for endpoint {endpoint}")
            queue = await surrealdb_handler.get_endpoint(endpoint, __file__)
            queue = queue["meta"]["_message_cache"]
            print(f"Queue: {queue}")
            if len(queue) == 0:
                return False
            elif len(queue) == 1:
                message = queue[0]
                print(f"Loading message {message}")
                updated = await surrealdb_handler.QueueHandler.loadMessage(endpoint, message)
                await sending_handler.SendingHandler.distribute(endpoint, updated)
                await cls.clearLoadedMessage(endpoint, message)
                return True
            elif len(queue) > 1:
                if len(queue) > 10:
                    await surrealdb_handler.QueueHandler.clear_queue(endpoint)
                    raise Exception("Queue length is too long. Clearing queue.")
                for message in queue:
                    updated = await surrealdb_handler.QueueHandler.loadMessage(endpoint, message)
                    await sending_handler.SendingHandler.distribute(endpoint, updated)
                    await cls.clearLoadedMessage(endpoint, message)
                return True
            else:
                raise Exception("Unknown error in sendMessage while processing queue. Queue length is unsupported type or negative.")
        except:
            try:
                await surrealdb_handler.QueueHandler.remove_from_queue(endpoint, message)
                await cls.clearLoadedMessage(endpoint, message)
            except:
                await surrealdb_handler.QueueHandler.clear_queue(endpoint)
            raise Exception("Error in sendMessage while processing queue.")


    @classmethod
    async def handleUpdatedEndpointData(cls, endpoint, updated_json):
        appended = await cls.appendMessage(endpoint, updated_json)
        if appended:
            asyncio.create_task(cls.sendMessage(endpoint))
            print("Appended message to queue and sent.")
        else:
            print("Failed to append message to queue.")
