import threading
import time
import asyncio
from astroidapi import surrealdb_handler, sending_handler
import logging
import json
import os


class QueueProcessor:    
    @classmethod
    async def appendMessage(cls, endpoint, updated_json):
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
        print(f"Sending message for endpoint {endpoint}")
        queue = await surrealdb_handler.QueueHandler.get_queue(endpoint)
        print(f"Queue: {queue}")
        if len(queue) == 0:
            return False
        elif len(queue) == 1:
            message = queue[0]
            print(f"Loading message {message}")
            updated = await surrealdb_handler.QueueHandler.loadMessage(endpoint, message)
            await sending_handler.SendingHandler.distribute(endpoint, updated)
            return True
        elif len(queue) > 1:
            for message in queue:
                updated = await surrealdb_handler.QueueHandler.loadMessage(endpoint, message)
                await sending_handler.SendingHandler.distribute(endpoint, updated)
            return True
        else:
            raise Exception("Unknown error in sendMessage while processing queue. Queue length is unsupported type or negative.")
        
    @classmethod
    async def handleUpdatedEndpointData(cls, endpoint, updated_json):
        await cls.appendMessage(endpoint, updated_json)
        await cls.sendMessage(endpoint)
        