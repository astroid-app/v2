import asyncio
import json
import logging
import pathlib
import re
import traceback
import fastapi
import astroidapi.sending_handler as sending_handler
import astroidapi.surrealdb_handler as surrealdb_handler
from Bot import config

class UpdateHandler:

    @classmethod
    async def update_endpoint(
        cls,
        endpoint: int,
        token: str = None,
        webhook_discord: str = None,
        webhook_guilded: str = None,
        webhook_revolt: str = None,
        webhook_nerimity: str = None,
        selfuse: bool = None,
        log_discord: str = None,
        log_guilded: str = None,
        log_revolt: str = None,
        log_nerimity: str = None,
        channel_discord: str = None,
        channel_guilded: str = None,
        channel_revolt: str = None,
        channel_nerimity: str = None,
        blacklist: str = None,
        trigger: bool = None,
        sender_channel: str = None,
        sender: str = None,
        message_author_name: str = None,
        message_author_avatar: str = None,
        allowed_ids: str = None,
        message_author_id: str = None,
        message_content: str = None,
        message_attachments: str = None,
        message_embed: str = None,
        beta: bool = False,
        index: int = None,
        only_check: bool = False,
    ):
        try:
            data_token = json.load(open(f"{pathlib.Path(__file__).parent.parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]

            if token is not None:
                if token == config.MASTER_TOKEN or token == data_token:
                    endpoint_data = await surrealdb_handler.get_endpoint(endpoint)
                    if endpoint_data:
                        if only_check:
                            if endpoint_data["meta"]["read"]["discord"] and endpoint_data["meta"]["read"]["guilded"] and endpoint_data["meta"]["read"]["revolt"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "All endpoints are read."})
                            else:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "Not all endpoints are read."})

                        if beta is True:
                            endpoint_data["config"]["isbeta"] = True

                        if webhook_discord:
                            if webhook_discord in endpoint_data["config"]["webhooks"]["discord"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This webhook already exists."})
                            elif index is not None:
                                endpoint_data["config"]["webhooks"]["discord"][index] = webhook_discord
                            else:
                                endpoint_data["config"]["webhooks"]["discord"].append(webhook_discord)

                        if webhook_guilded:
                            if webhook_guilded in endpoint_data["config"]["webhooks"]["guilded"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This webhook already exists."})
                            elif index is not None:
                                endpoint_data["config"]["webhooks"]["guilded"][index] = webhook_guilded
                            else:
                                endpoint_data["config"]["webhooks"]["guilded"].append(webhook_guilded)

                        if webhook_revolt:
                            if webhook_revolt in endpoint_data["config"]["webhooks"]["revolt"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This webhook already exists."})
                            elif index is not None:
                                endpoint_data["config"]["webhooks"]["revolt"][index] = webhook_revolt
                            else:
                                endpoint_data["config"]["webhooks"]["revolt"].append(webhook_revolt)
                        
                        if webhook_nerimity:
                            if webhook_nerimity in endpoint_data["config"]["webhooks"]["nerimity"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This webhook already exists."})
                            elif index is not None:
                                endpoint_data["config"]["webhooks"]["nerimity"][index] = webhook_nerimity
                            else:
                                endpoint_data["config"]["webhooks"]["nerimity"].append(webhook_nerimity)

                        if selfuse is True or selfuse is False:
                            endpoint_data["config"]["self-user"] = selfuse

                        if log_discord:
                            endpoint_data["config"]["logs"]["discord"] = log_discord

                        if log_guilded:
                            endpoint_data["config"]["logs"]["guilded"] = log_guilded

                        if log_revolt:
                            endpoint_data["config"]["logs"]["revolt"] = log_revolt
                        
                        if log_nerimity:
                            endpoint_data["config"]["logs"]["nerimity"] = log_nerimity

                        if channel_discord:
                            if channel_discord in endpoint_data["config"]["channels"]["discord"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This channel already exists."})
                            elif index is not None:
                                endpoint_data["config"]["channels"]["discord"][index] = channel_discord
                            else:
                                endpoint_data["config"]["channels"]["discord"].append(channel_discord)

                        if channel_guilded:
                            if channel_guilded in endpoint_data["config"]["channels"]["guilded"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This channel already exists."})
                            elif index is not None:
                                endpoint_data["config"]["channels"]["guilded"][index] = channel_guilded
                            else:
                                endpoint_data["config"]["channels"]["guilded"].append(channel_guilded)

                        if channel_revolt:
                            if channel_revolt in endpoint_data["config"]["channels"]["revolt"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This channel already exists."})
                            elif index is not None:
                                endpoint_data["config"]["channels"]["revolt"][index] = channel_revolt
                            else:
                                endpoint_data["config"]["channels"]["revolt"].append(channel_revolt)
                        
                        if channel_nerimity:
                            if channel_nerimity in endpoint_data["config"]["channels"]["nerimity"]:
                                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This channel already exists."})
                            elif index is not None:
                                endpoint_data["config"]["channels"]["nerimity"][index] = channel_nerimity
                            else:
                                endpoint_data["config"]["channels"]["nerimity"].append(channel_nerimity)

                        if blacklist:
                            if "," in blacklist:
                                for val in blacklist.split(","):
                                    if val.lower() not in [x.lower() for x in endpoint_data["config"]["blacklist"]]:
                                        endpoint_data["config"]["blacklist"].append(val.lower())
                            else:
                                if blacklist.lower() not in endpoint_data["config"]["blacklist"]:
                                    if index is not None:
                                        endpoint_data["config"]["blacklist"][index] = blacklist.lower()
                                    else:
                                        endpoint_data["config"]["blacklist"].append(blacklist.lower())

                        if trigger:
                            endpoint_data["meta"]["trigger"] = trigger

                        if sender_channel:
                            endpoint_data["meta"]["sender-channel"] = sender_channel

                        if sender:
                            if sender in ["discord", "guilded", "revolt", "nerimity"]:
                                endpoint_data["meta"]["sender"] = sender
                                endpoint_data["meta"]["read"][sender] = True
                            else:
                                return fastapi.responses.JSONResponse(status_code=400, content={"message": "Invalid sender."})

                        if message_author_name:
                            endpoint_data["meta"]["message"]["author"]["name"] = message_author_name

                        if message_author_avatar:
                            endpoint_data["meta"]["message"]["author"]["avatar"] = message_author_avatar

                        if allowed_ids:
                            if "," in allowed_ids:
                                for val in allowed_ids.split(","):
                                    if val not in endpoint_data["config"]["allowed-ids"]:
                                        endpoint_data["config"]["allowed-ids"].append(val)
                            else:
                                if allowed_ids not in endpoint_data["config"]["allowed-ids"]:
                                    if index is not None:
                                        endpoint_data["config"]["allowed-ids"][index] = allowed_ids
                                    else:
                                        endpoint_data["config"]["allowed-ids"].append(allowed_ids)

                        if message_author_id:
                            endpoint_data["meta"]["message"]["author"]["id"] = message_author_id

                        if message_content:
                            if sender == "discord":
                                if "http" in message_content or "https" in message_content:
                                    urls = re.findall(r'(https?://\S+)', message_content)
                                    for url in urls:
                                        image_markdown = f"![{url}]({url})"
                                        message_content = message_content.replace(url, image_markdown) + message_content.split(url)[1]
                                endpoint_data["meta"]["message"]["content"] = message_content
                            else:
                                endpoint_data["meta"]["message"]["content"] = message_content

                        if message_attachments:
                            if "," in message_attachments:
                                for val in message_attachments.split(","):
                                    if val.lower() not in [x.lower() for x in endpoint_data["meta"]["message"]["attachments"]]:
                                        if sender == "discord":
                                            endpoint_data["meta"]["message"]["attachments"].append(f"![]({val})")
                                        else:
                                            endpoint_data["meta"]["message"]["attachments"].append(val)
                            else:
                                endpoint_data["meta"]["message"]["attachments"] = []

                        if message_embed:
                            embed_object = json.loads(message_embed.replace("'", '"'))
                            endpoint_data["meta"]["message"]["embed"] = embed_object
                        
                        if len(endpoint_data["config"]["channels"]["discord"]) == 0:
                            endpoint_data["meta"]["read"]["discord"] = True
                        if len(endpoint_data["config"]["channels"]["guilded"]) == 0:
                            endpoint_data["meta"]["read"]["guilded"] = True
                        if len(endpoint_data["config"]["channels"]["revolt"]) == 0:
                            endpoint_data["meta"]["read"]["revolt"] = True
                        if len(endpoint_data["config"]["channels"]["nerimity"]) == 0:
                            endpoint_data["meta"]["read"]["nerimity"] = True

                        updated_json = await surrealdb_handler.update(endpoint, endpoint_data)
                        try:
                            updated_json = updated_json[0]["result"][0]
                            updated_json.pop("id")
                        except:
                            pass
                        finally:
                            if not updated_json["config"]["self-user"] is True:                   
                                if updated_json["meta"]["trigger"]:
                                    await sending_handler.SendingHandler.distribute(endpoint)
                                    print("Distributed")
                                    waiting_secs = 0
                                    max_secs = 10
                                    while True:
                                        check_json = await surrealdb_handler.get_endpoint(endpoint)
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
                                            check_json["meta"]["read"]["discord"] = False
                                            check_json["meta"]["read"]["guilded"] = False
                                            check_json["meta"]["read"]["revolt"] = False
                                            check_json["meta"]["read"]["nerimity"] = False
                                            await surrealdb_handler.update(endpoint, check_json)
                                            print("Not everything is read. Cleared anyways.")
                                            break

                                else:
                                    return fastapi.responses.JSONResponse(
                                        status_code=200,
                                        content={"message": "This endpoint activated self-usage."},
                                    )

                        return fastapi.responses.JSONResponse(status_code=200, content=endpoint_data)
                    else:
                        return fastapi.responses.JSONResponse(status_code=404, content={"message": "This endpoint does not exist."})
                else:
                    return fastapi.responses.JSONResponse(status_code=401, content={"message": "The provided token is invalid."})
            else:
                return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})
        except IndexError:
            waiting_secs = 0
            max_secs = 10
            while True:
                check_json = await surrealdb_handler.get_endpoint(endpoint)
                if check_json["meta"]["trigger"] is False and check_json["meta"]["message"]["content"] is None:
                    return fastapi.responses.JSONResponse(status_code=200, content=check_json)
                if (check_json["meta"]["read"]["discord"] == True
                        and check_json["meta"]["read"]["guilded"] == True
                        and check_json["meta"]["read"]["revolt"] == True
                        and check_json["meta"]["read"]["nerimity"] == True and check_json["config"]["self-user"] is False):
                    check_json["meta"]["message"]["content"] = None
                    check_json["meta"]["message"]["attachments"].clear()
                    check_json["meta"]["message"]["author"]["avatar"] = None
                    check_json["meta"]["message"]["author"]["name"] = None
                    check_json["meta"]["message"]["author"]["id"] = None
                    check_json["meta"]["trigger"] = False
                    check_json["meta"]["sender"] = None
                    check_json["meta"]["sender-channel"] = None
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
                    check_json["meta"]["read"]["discord"] = False
                    check_json["meta"]["read"]["guilded"] = False
                    check_json["meta"]["read"]["revolt"] = False
                    check_json["meta"]["read"]["nerimity"] = False
                    await surrealdb_handler.update(endpoint, check_json)
                    print("Not everything is read. Cleared anyways.")
                    break

                elif check_json["config"]["self-user"] is True:
                    return fastapi.responses.JSONResponse(
                        status_code=200,
                        content={"message": "This endpoint activated self-usage."},
                    )
        except Exception as e:
            logging.error("An error occurred: %s", e)
            logging.error(traceback.format_exc())
            return fastapi.responses.JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})



class Validator:

    @classmethod
    async def validate_endpoint(cls, endpoint: int, token: str = None):
        healthy_endpoint_data = {
            "config": {
                "self-user": False,
                "webhooks": {
                    "discord": [],
                    "guilded": [],
                    "revolt": [],
                    "nerimity": []
                },
                "channels": {
                    "discord": [],
                    "guilded": [],
                    "revolt": [],
                    "nerimity": []
                },
                "logs": {
                    "discord": None,
                    "guilded": None,
                    "revolt": None,
                    "nerimity": None
                },
                "blacklist": [],
                "allowed-ids": [],
                "isbeta": False
            },
            "meta": {
                "sender-channel": None,
                "trigger": False,
                "sender": None,
                "read": {
                    "discord": False,
                    "guilded": False,
                    "revolt": False,
                    "nerimity": False
                },
                "message": {
                    "author": {
                        "name": None,
                        "avatar": None,
                        "id": None
                    },
                    "content": None,
                    "attachments": []
                }
            }
        }
        endpoint_data = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r"))
        if token is not None:
            if token == config.MASTER_TOKEN:
                if endpoint_data == healthy_endpoint_data:
                    return fastapi.responses.JSONResponse(status_code=200, content={"message": "Endpoint is healthy."})
                else:
                    return fastapi.responses.JSONResponse(status_code=400, content={"message": "Endpoint is not healthy."})
            else:
                return fastapi.responses.JSONResponse(status_code=401, content={"message": "The provided token is invalid."})
        else:
            return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})