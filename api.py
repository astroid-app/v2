import asyncio
import json
import os
import pathlib
import traceback
import aiohttp
import uvicorn
import fastapi
import nextcord
import guilded
import Bot.config
import fastapi.security
import secrets
from typing import Annotated

api = fastapi.FastAPI(
    title="Guildcord API",
    description="Guildcord API for getting and modifying endpoints.",
    version="2.1.3",
)


@api.get("/", description="Does nothing. Just sitting there and waiting for requests. (Redirects on 'GET' to the "
                          "documentation.)")
def root():
    return fastapi.responses.RedirectResponse(status_code=301, url="https://guildcord-api.tk/docs")


@api.get("/{endpoint}", description="Get an endpoint.")
def get_endpoint(endpoint: int,
                 token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
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
                return fastapi.responses.Response(status_code=404, content="This endpoint does not exist.")
        else:
            return fastapi.responses.Response(status_code=401, content="the provided token is invalid.")
    else:
        return fastapi.responses.Response(status_code=401, content="You must provide a token.")


@api.get("/bridges/{endpoint}", description="Get an endpoint.")
def get_endpoint(endpoint: int,
                 token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    global data_token
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    except:
        data_token = None
        pass
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                bridges_json = json.load(
                    open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r"))
                bridges_discord = []
                bridges_guilded = []
                bridges_revolt = []
                for bridge in bridges_json["config"]["channels"]["discord"]:
                    bridges_discord.append(bridge)
                for bridge in bridges_json["config"]["channels"]["revolt"]:
                    bridges_revolt.append(bridge)
                for bridge in bridges_json["config"]["channels"]["guilded"]:
                    bridges_guilded.append(bridge)

                return
            except FileNotFoundError:
                return fastapi.responses.Response(status_code=404, content="This endpoint does not exist.")
        else:
            return fastapi.responses.Response(status_code=401, content="the provided token is invalid.")
    else:
        return fastapi.responses.Response(status_code=401, content="You must provide a token.")


@api.post("/token/{endpoint}", description="Generate a new token. (Only works with Guildcord-Bot)")
def new_token(endpoint: int,
              master_token: Annotated[str, fastapi.Query(max_length=85, min_length=85)]):
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
        return fastapi.responses.Response(status_code=403, content="The provided token is invalid.")


@api.post("/update/{endpoint}", description="Modify an endpoint.",
          response_description="Endpoint with updated data.")
async def post_endpoint(endpoint: int,
                        webhook_discord: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        webhook_guilded: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        webhook_revolt: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        log_discord: Annotated[int, fastapi.Query(max_length=25, min_length=10)] = None,
                        log_guilded: Annotated[str, fastapi.Query(max_length=8, min_length=50)] = None,
                        log_revolt: Annotated[str, fastapi.Query(max_length=8, min_length=50)] = None,
                        channel_discord: Annotated[int, fastapi.Query(max_length=25, min_length=10)] = None,
                        channel_guilded: Annotated[str, fastapi.Query(max_length=150, min_length=10)] = None,
                        channel_revolt: Annotated[str, fastapi.Query(max_length=50, min_length=8)] = None,
                        blacklist: Annotated[str, fastapi.Query(max_length=250, min_length=1)] = None,
                        sender_channel: Annotated[str, fastapi.Query(max_length=80, min_length=10)] = None,
                        trigger: bool = None,
                        sender: Annotated[str, fastapi.Query(max_length=10, min_length=5)] = None,
                        message_author_name: Annotated[str, fastapi.Query(max_length=50, min_length=1)] = None,
                        message_author_avatar: Annotated[str, fastapi.Query(max_length=250, min_length=50)] = None,
                        allowed_ids: Annotated[str, fastapi.Query(max_length=50, min_length=10)] = None,
                        message_author_id: Annotated[str, fastapi.Query(max_length=50, min_length=10)] = None,
                        message_content: Annotated[str, fastapi.Query(max_length=1500)] = None,
                        message_attachments: Annotated[str, fastapi.Query(max_length=1550, min_length=50)] = None,
                        selfuse: bool = None,
                        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            if f"{endpoint}.json" in os.listdir(f"{pathlib.Path(__file__).parent.resolve()}/endpoints"):
                file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+")
                json_file = json.load(file)
                if webhook_discord:
                    json_file["config"]["webhooks"]["discord"].append(webhook_discord)
                if webhook_guilded:
                    json_file["config"]["webhooks"]["guilded"].append(webhook_guilded)
                if webhook_revolt:
                    json_file["config"]["webhooks"]["revolt"].append(webhook_revolt)
                if selfuse is True or selfuse is False:
                    json_file["config"]["self-user"] = selfuse
                if log_discord:
                    json_file["config"]["logs"]["discord"] = log_discord
                if log_guilded:
                    json_file["config"]["logs"]["guilded"] = log_guilded
                if log_revolt:
                    json_file["config"]["logs"]["revolt"] = log_revolt
                if channel_discord:
                    json_file["config"]["channels"]["discord"].append(channel_discord)
                if channel_guilded:
                    json_file["config"]["channels"]["guilded"].append(channel_guilded)
                if channel_revolt:
                    json_file["config"]["channels"]["revolt"].append(channel_revolt)
                if blacklist:
                    if "," in blacklist:
                        for val in blacklist.split(","):
                            for in_value in json_file["config"]["blacklist"]:
                                if val.lower() == in_value.lower():
                                    return fastapi.responses.Response(status_code=200)
                            else:
                                json_file["config"]["blacklist"].append(val.lower())
                    else:
                        json_file["config"]["blacklist"].append(blacklist.lower())
                if trigger:
                    json_file["meta"]["trigger"] = trigger
                if sender_channel:
                    json_file["meta"]["sender-channel"] = sender_channel
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
                    if "," in allowed_ids:
                        for val in allowed_ids.split(","):
                            if val in json_file["config"]["allowed_ids"]:
                                return fastapi.responses.Response(status_code=200)
                            else:
                                json_file["config"]["allowed_ids"].append(val)
                    else:
                        json_file["config"]["allowed_ids"].append(allowed_ids)
                if message_author_id:
                    json_file["meta"]["message"]["author"]["id"] = message_author_id
                if message_content:
                    json_file["meta"]["message"]["content"] = message_content
                if message_attachments:
                    if "," in message_attachments:
                        for val in message_attachments.split(","):
                            for in_value in json_file["meta"]["message"]["attachments"]:
                                if val.lower() == in_value.lower():
                                    return fastapi.responses.Response(status_code=200)
                            else:
                                json_file["meta"]["message"]["attachments"].append(val)
                    else:
                        json_file["meta"]["message"]["attachments"].append(message_attachments)
                file.seek(0)
                json.dump(json_file, file)
                file.truncate()
                file.close()
                updated_file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+")
                updated_json = json.load(updated_file)
                if updated_json["config"]["self-user"] is False:
                    sender = updated_json["meta"]["sender"]

                    if sender == "discord":
                        session = aiohttp.ClientSession()
                        updated_json["meta"]["read"]["discord"] = True
                        global webhook_url_g
                        for channel in updated_json["config"]["channels"]["discord"]:
                            if str(channel) == updated_json["meta"]["sender-channel"]:
                                webhook_url_g = updated_json["config"]["webhooks"]["guilded"][
                                    updated_json["config"]["channels"]["discord"].index(int(channel))]
                                if message_content:
                                    await guilded.Webhook.from_url(webhook_url_g, session=session).send(
                                        content=updated_json["meta"]["message"]["content"],
                                        avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                        username=updated_json["meta"]["message"]["author"]["name"]
                                    )
                                if updated_json["meta"]["message"]["attachments"]:
                                    for attachment in updated_json["meta"]["message"]["attachments"]:
                                        await guilded.Webhook.from_url(webhook_url_g, session=session).send(
                                            content=attachment,
                                            avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                            username=updated_json["meta"]["message"]["author"]["name"]
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
                        session = aiohttp.ClientSession()
                        updated_json["meta"]["read"]["guilded"] = True
                        global webhook_url_d
                        for channel in updated_json["config"]["channels"]["guilded"]:
                            if str(channel) == updated_json["meta"]["sender-channel"]:
                                webhook_url_d = updated_json["config"]["webhooks"]["discord"][
                                    updated_json["config"]["channels"]["guilded"].index(str(channel))]
                                if message_content:
                                    await nextcord.Webhook.from_url(webhook_url_d, session=session).send(
                                        content=updated_json["meta"]["message"]["content"],
                                        avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                        username=updated_json["meta"]["message"]["author"]["name"]
                                    )
                                if updated_json["meta"]["message"]["attachments"]:
                                    for attachment in updated_json["meta"]["message"]["attachments"]:
                                        await nextcord.Webhook.from_url(webhook_url_d, session=session).send(
                                            content=f"![]({attachment})",
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
                        global discord_webhook_url
                        if str(updated_json["meta"]["sender-channel"]) in updated_json["config"]["channels"]["revolt"]:
                            discord_webhook_url = updated_json["config"]["webhooks"]["discord"][
                                updated_json["config"]["channels"]["revolt"].index(
                                    str(updated_json["meta"]["sender-channel"]))]
                            print(discord_webhook_url)
                            if message_content:
                                await nextcord.Webhook.from_url(discord_webhook_url, session=session).send(
                                    content=updated_json["meta"]["message"]["content"],
                                    avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                    username=updated_json["meta"]["message"]["author"]["name"]
                                )
                            if updated_json["meta"]["message"]["attachments"]:
                                for attachment in updated_json["meta"]["message"]["attachments"]:
                                    await nextcord.Webhook.from_url(discord_webhook_url, session=session).send(
                                        content=attachment,
                                        avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                        username=updated_json["meta"]["message"]["author"]["name"]
                                    )
                            updated_json["meta"]["read"]["discord"] = True
                        global guilded_webhook_url
                        if str(updated_json["meta"]["sender-channel"]) in str(
                                updated_json["config"]["channels"]["revolt"]):
                            guilded_webhook_url = updated_json["config"]["webhooks"]["guilded"][
                                updated_json["config"]["channels"]["revolt"].index(
                                    str(updated_json["meta"]["sender-channel"]))]
                            if message_content:
                                await guilded.Webhook.from_url(guilded_webhook_url, session=session).send(
                                    content=updated_json["meta"]["message"]["content"],
                                    avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                    username=updated_json["meta"]["message"]["author"]["name"]
                                )
                            if updated_json["meta"]["message"]["attachments"]:
                                for attachment in updated_json["meta"]["message"]["attachments"]:
                                    await guilded.Webhook.from_url(guilded_webhook_url, session=session).send(
                                        content=f"![]({attachment})",
                                        avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                        username=updated_json["meta"]["message"]["author"]["name"]
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
                        if check_json["meta"]["read"]["discord"] == True and check_json["meta"]["read"][
                            "guilded"] == True and check_json["meta"]["read"]["revolt"] == True:
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
                            check_file.seek(0)
                            json.dump(check_json, check_file)
                            check_file.truncate()
                            check_file.close()
                            break
                        check_file.close()
                        await asyncio.sleep(1)
                else:
                    return fastapi.responses.Response(status_code=200, content="This endpoint activated self-usage.")
        else:
            return fastapi.responses.Response(status_code=401, content="The provided token is invalid.")
    else:
        return fastapi.responses.Response(status_code=401, content="You must provide a token.")


@api.post("/read/{endpoint}",
          description="Mark the 'meta' as read on the platform(s). "
                      "[Note: Currently only used in the Guildcord Revolt-bot.]")
def mark_read(endpoint: int,
              token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
              read_discord: bool = None,
              read_guilded: bool = None,
              read_revolt: bool = None):
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
        return fastapi.responses.Response(status_code=401, content="The provided token is invalid.")


@api.post("/create", description="Create an endpoint.",
          response_description="Endpoints data.")
def create_endpoint(endpoint: int):
    try:
        file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "x")
        data = {
            "config": {
                "self-user": False,
                "webhooks": {
                    "discord": [],
                    "guilded": [],
                    "revolt": []
                },
                "channels": {
                    "discord": [],
                    "guilded": [],
                    "revolt": []
                },
                "logs": {
                    "discord": None,
                    "guilded": None,
                    "revolt": None
                },
                "blacklist": [],
                "allowed-ids": []
            },
            "meta": {
                "sender-channel": None,
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
                    "attachments": []
                }
            }
        }
        json.dump(data, file)
        return fastapi.responses.Response(status_code=201, content="Created.")
    except FileExistsError:
        return fastapi.responses.Response(status_code=403, content="This endpoint exists already.")


@api.delete("/delete/{endpoint}", description="Delete an endpoint.")
def delete_endpoint(endpoint: int,
                    token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                os.remove(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json")
            except FileNotFoundError:
                return fastapi.responses.Response(status_code=404, content="This endpoint does not exist.")
        else:
            return fastapi.responses.Response(status_code=401, content="The provided token is invalid.")
    else:
        return fastapi.responses.Response(status_code=401, content="You must provide a token.")


uvicorn.run(api, host="localhost", port=991)
