import asyncio
import json
import os
import pathlib
import traceback
import aiohttp
import uvicorn
import fastapi
import requests
import nextcord
import guilded
import Bot.config
import fastapi.security
import secrets

api = fastapi.FastAPI(
    title="Guildcord API",
    description="Guildcord API for getting and modifying endpoints.",
    version="2.0.0",

)


@api.get("/", description="Does nothing. Just sitting there and waiting for requests.")
def root():
    return {"status": 200, "message": "Just sittin'. See our docs: http://guildcord-api.tk/docs"}


@api.get("/{endpoint}", description="Get an endpoint.")
def get_endpoint(endpoint: int, token: str | None):
    global data_token
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    except:
        data_token = None
        pass
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                return json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r"))
            except FileNotFoundError:
                return fastapi.responses.Response(status_code=404)
        else:
            return fastapi.responses.Response(status_code=401)
    else:
        return fastapi.responses.Response(status_code=401)


@api.post("/token/{endpoint}", description="Generate a new token. (Only works with Guildcord-Bot)")
def new_token(endpoint: int, master_token: str):
    if master_token == Bot.config.MASTER_TOKEN:
        with open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r+") as tokens:
            token = secrets.token_urlsafe(53)
            print(token)
            data = json.load(tokens)
            data[f"{endpoint}"] = token
            tokens.seek(0)
            json.dump(data, tokens)
            tokens.truncate()
            tokens.close()
            return {f"token": token}

    else:
        return fastapi.responses.Response(status_code=403)


@api.post("/update/{endpoint}", description="Modify an endpoint. 'data'-Parameter must be [].",
          response_description="Endpoint with updated data.")
async def post_endpoint(endpoint: int,
                        webhook_discord: str = None, webhook_guilded: str = None, log_discord: int = None,
                        log_guilded: str = None, channel_discord: int = None, channel_guilded: str = None,
                        channel_revolt: str = None,
                        blacklist: str = None,
                        trigger: bool = None, sender: str = None, message_author_name: str = None,
                        message_author_avatar: str = None, allowed_ids: str = None,
                        message_author_id: str = None, message_content: str = None, message_attachments: list = None,
                        selfuse: bool = None, *, token: str | None):
    data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            if f"{endpoint}.json" in os.listdir(f"{pathlib.Path(__file__).parent.resolve()}/endpoints"):
                file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+")
                json_file = json.load(file)
                if webhook_discord:
                    json_file["config"]["webhooks"]["discord"] = webhook_discord
                if webhook_guilded:
                    json_file["config"]["webhooks"]["guilded"] = webhook_guilded
                if selfuse is True or selfuse is False:
                    json_file["config"]["self-user"] = selfuse
                if log_discord:
                    json_file["config"]["logs"]["discord"] = log_discord

                if log_guilded:
                    json_file["config"]["logs"]["guilded"] = log_guilded

                if channel_discord:
                    json_file["config"]["channels"]["discord"] = channel_discord
                if channel_guilded:
                    json_file["config"]["channels"]["guilded"] = channel_guilded
                if channel_revolt:
                    json_file["config"]["channels"]["revolt"] = channel_revolt
                if blacklist:
                    print(blacklist)
                    json_file["config"]["blacklist"].append(blacklist)
                if trigger:
                    json_file["meta"]["trigger"] = trigger
                if sender:
                    if sender == "discord":
                        json_file["meta"]["sender"] = "discord"
                    elif sender == "guilded":
                        json_file["meta"]["sender"] = "guilded"
                    elif sender == "revolt":
                        json_file["meta"]["sender"] = "revolt"
                    else:
                        return fastapi.responses.Response(status_code=400)
                if message_author_name:
                    json_file["meta"]["message"]["author"]["name"] = message_author_name
                if message_author_avatar:
                    json_file["meta"]["message"]["author"]["avatar"] = message_author_avatar
                if allowed_ids:
                    json_file["config"]["allowed-ids"].append(allowed_ids)
                if message_author_id:
                    json_file["meta"]["message"]["author"]["id"] = message_author_id
                if message_content:
                    json_file["meta"]["message"]["content"] = message_content
                if message_attachments:
                    json_file["meta"]["message"]["attachments"] = message_attachments

                file.seek(0)
                json.dump(json_file, file)
                file.truncate()
                file.close()
                updated_file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+")
                updated_json = json.load(updated_file)
                if not updated_json["config"]["self-user"] is True and updated_json["meta"]["trigger"] is True:
                    sender = updated_json["meta"]["sender"]

                    if sender == "discord":
                        updated_json["meta"]["sender"] = None
                        session = aiohttp.ClientSession()
                        updated_json["meta"]["read"]["discord"] = True
                        webhook_url = updated_json["config"]["webhooks"]["guilded"]
                        await guilded.Webhook.from_url(webhook_url, session=session).send(
                            content=updated_json["meta"]["message"]["content"],
                            avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                            username=updated_json["meta"]["message"]["author"]["name"],
                        )
                        await session.close()
                        updated_json["meta"]["read"]["guilded"] = True
                        if not updated_json["config"]["channels"]["revolt"]:
                            updated_json["meta"]["read"]["revolt"] = True
                        if not updated_json["config"]["channels"]["guilded"]:
                            updated_json["meta"]["read"]["guilded"] = True
                        updated_file.seek(0)
                        json.dump(updated_json, updated_file)
                        updated_file.truncate()

                    elif sender == "guilded":
                        updated_json["meta"]["sender"] = None
                        session = aiohttp.ClientSession()
                        updated_json["meta"]["read"]["guilded"] = True
                        webhook_url = updated_json["config"]["webhooks"]["discord"]
                        await nextcord.Webhook.from_url(webhook_url, session=session).send(
                            content=updated_json["meta"]["message"]["content"],
                            avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                            username=updated_json["meta"]["message"]["author"]["name"]
                        )
                        await session.close()
                        updated_json["meta"]["read"]["discord"] = True
                        if not updated_json["config"]["channels"]["revolt"]:
                            updated_json["meta"]["read"]["revolt"] = True
                        if not updated_json["config"]["channels"]["discord"]:
                            updated_json["meta"]["read"]["discord"] = True
                        updated_file.seek(0)
                        json.dump(updated_json, updated_file)
                        updated_file.truncate()

                    elif sender == "revolt":
                        session = aiohttp.ClientSession()
                        updated_json["meta"]["read"]["revolt"] = True
                        discord_webhook_url = updated_json["config"]["webhooks"]["discord"]
                        await nextcord.Webhook.from_url(discord_webhook_url, session=session).send(
                            content=updated_json["meta"]["message"]["content"],
                            avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                            username=updated_json["meta"]["message"]["author"]["name"],
                        )
                        updated_json["meta"]["read"]["discord"] = True
                        guilded_webhook_url = updated_json["config"]["webhooks"]["guilded"]
                        await guilded.Webhook.from_url(guilded_webhook_url, session=session).send(
                            content=updated_json["meta"]["message"]["content"],
                            avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                            username=updated_json["meta"]["message"]["author"]["name"],
                        )
                        await session.close()
                        updated_json["meta"]["read"]["guilded"] = True
                        if not updated_json["config"]["channels"]["guilded"]:
                            updated_json["meta"]["read"]["guilded"] = True
                        if not updated_json["config"]["channels"]["discord"]:
                            updated_json["meta"]["read"]["discord"] = True
                        updated_file.seek(0)
                        json.dump(updated_json, updated_file)
                        updated_file.truncate()

                    updated_file.close()
                    while True:
                        check_file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                                            "r+")
                        check_json = json.load(check_file)
                        if check_json["meta"]["read"]["discord"] == True and check_json["meta"]["read"]["guilded"] == True and check_json["meta"]["read"]["revolt"] == True:
                            check_json["meta"]["message"]["content"] = None
                            check_json["meta"]["message"]["author"]["avatar"] = None
                            check_json["meta"]["message"]["author"]["name"] = None
                            check_json["meta"]["message"]["author"]["id"] = None
                            check_json["meta"]["trigger"] = False
                            check_json["meta"]["sender"] = None
                            check_json["meta"]["read"]["discord"] = False
                            check_json["meta"]["read"]["guilded"] = False
                            check_json["meta"]["read"]["revolt"] = False
                            check_file.seek(0)
                            json.dump(check_json, check_file)
                            check_file.truncate()
                            check_file.close()
                            break
                        check_file.close()
                        await asyncio.sleep(1)
                return fastapi.responses.Response(status_code=404)
        else:
            return fastapi.responses.Response(status_code=401)
    else:
        return fastapi.responses.Response(status_code=401)



@api.post("/read/{endpoint}")
def mark_read(endpoint: int, token: str | None, read_discord: bool = None, read_guilded: bool = None, read_revolt: bool = None):
    if token == data_token or token == Bot.config.MASTER_TOKEN:
        file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+")
        json_file = json.load(file)
        if read_discord:
            json_file["meta"]["read"]["discord"] = True
        if read_guilded:
            json_file["meta"]["read"]["guilded"] = True
        if read_revolt:
            json_file["meta"]["read"]["revolt"] = True
        try:
            file.seek(0)
            json.dump(json_file, file)
            file.truncate()
            file.close()
        except:
            traceback.print_exc()
    else:
        return fastapi.responses.Response(status_code=401)


@api.post("/create", description="Create an endpoint.",
          response_description="Endpoints data.")
def create_endpoint(endpoint: int):
    try:
        file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "x")
        data = {
            "config": {
                "self-user": False,
                "webhooks": {
                    "discord": None,
                    "guilded": None,
                    "revolt": None
                },
                "channels": {
                    "discord": None,
                    "guilded": None,
                    "revolt": None
                },
                "logs": {
                    "discord": None,
                    "guilded": None
                },
                "blacklist": [
                ],
                "allowed-ids": [

                ]
            },
            "meta": {
                "trigger": False,
                "sender": None,
                "read": {
                    "discord": False,
                    "guilded": False,
                    "revolt": False
                },
                "message": {
                    "author": {
                        "name": None,
                        "avatar": None,
                        "id": None
                    },
                    "content": None,
                    "attachments": [
                        None
                    ]
                }
            }
        }
        json.dump(data, file)
        return fastapi.responses.Response(status_code=201)
    except FileExistsError:
        return fastapi.responses.Response(status_code=403)


@api.delete("/delete/{endpoint}", description="Delete you API endpoint.")
def delete_endpoint(endpoint: int, token: str | None):
    data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                os.remove(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json")
            except FileNotFoundError:
                return fastapi.responses.Response(status_code=404)
        else:
            return fastapi.responses.Response(status_code=401)
    else:
        return fastapi.responses.Response(status_code=401)


uvicorn.run(api, host="localhost", port=991)
