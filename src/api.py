import asyncio
import json
import os
import asyncio
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
from typing import Annotated, Optional, List
import re
import beta_users
from fastapi.middleware.cors import CORSMiddleware
import requests
import sentry_sdk
import PIL
from PIL import Image
from fastapi import HTTPException, Response
from pydantic import BaseModel, Field

sentry_sdk.init(
    dsn=Bot.config.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


api = fastapi.FastAPI(
    title="Astroid API",
    description="Astroid API for getting and modifying endpoints.",
    version="2.1.4",
    docs_url=None
)


api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/assets/{asset}", description="Get an asset.")
def get_asset(asset: str, width: int = None, height: int = None):
    if not width and not height:
        try:
            return fastapi.responses.FileResponse(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/{asset}")
        except FileNotFoundError:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This asset does not exist."})
    else:
        print(width, height)
        if asset == "logo_no_bg":
            image = Image.open(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/Astroid Logo no bg.png")
            new_image = image.resize((width, height))
            new_image.save(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/resized/Astroid Logo no bg.png")
            return fastapi.responses.FileResponse(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/resized/Astroid Logo no bg{width}x{height}.png")
        elif asset == "logo":
            image = Image.open(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/Astroid Logo.png")
            new_image = image.resize((width, height))
            new_image.save(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/resized/Astroid Logo.png")
            return fastapi.responses.FileResponse(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/resized/Astroid Logo{width}x{height}.png")
        elif asset == "banner":
            image = Image.open(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/resized/Astroid-banner.png")
            new_image = image.resize((width, height))
            new_image.save(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/resized/Astroid-banner.png")
            return fastapi.responses.FileResponse(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/resized/Astroid-banner{width}x{height}.png")
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This asset does not exist."})

@api.get("/docs", description="Get the documentation.")
def docs():
    return fastapi.responses.RedirectResponse(status_code=301, url="https://docs.astroid.deutscher775.de")

@api.get("/", description="Home.")
def root():
    home_data = {
        "heading": "Astroid API",
        "description": "Astroid API for getting and modifying endpoints.",
        "privacy": "https://astroid.deutscher775.de/privacy",
        "terms": "https://astroid.deutscher775.de/terms",
        "imprint": "https://deutscher775.de/imprint.html",
        "docs": "https://astroid.deutscher775.de/docs",
        "discord": "https://discord.gg/DbrFADj6Xw",

    }
    return fastapi.responses.JSONResponse(status_code=200, content=home_data)

@api.get("/invite/{platform}", description="Get the invite link for the astroid bot.")
def invite(platform: str, token: Annotated[str, fastapi.Query(max_length=85)] = None):
    if platform == "discord":
        return fastapi.responses.RedirectResponse(status_code=301, url="https://discord.com/oauth2/authorize?client_id=1046057269202268303&permissions=2687625280&scope=bot%20applications.commands")
    elif platform == "guilded":
        return fastapi.responses.RedirectResponse(status_code=301, url="https://www.guilded.gg/b/00c19caa-e176-45f6-b1f6-7bee5ba73db9")
    elif platform == "discord-beta" and token in beta_users.TOKENS:
        return fastapi.responses.RedirectResponse(status_code=301, url="https://discord.com/oauth2/authorize?client_id=1230579871059804280&permissions=138046467089&scope=applications.commands+bot")
    elif platform == "guilded-beta" and token in beta_users.TOKENS:
        return fastapi.responses.RedirectResponse(status_code=301, url="https://www.guilded.gg/b/3f887186-82d5-4fe1-abbd-045748b125b3")
    else:
        return fastapi.responses.JSONResponse(status_code=400, content={"message": "Invalid platform."})

@api.get("/discord", description="Discord Server")
def discord():
    return fastapi.responses.RedirectResponse(
        status_code=301,
        url="https://discord.gg/DbrFADj6Xw"
    )

@api.get("/privacy", description="Privacy")
def privacy():
    return fastapi.responses.FileResponse(f"{pathlib.Path(__file__).parent.resolve()}/website/privacy.html")

@api.get("/terms", description="Terms of service")
def terms():
    return fastapi.responses.FileResponse(f"{pathlib.Path(__file__).parent.resolve()}/website/terms.html")

@api.get("/imprint", description="Imprint")
def imprint():
    return fastapi.responses.RedirectResponse("https://deutscher775.de/imprint")

@api.get("/docs/props", description="Get the properties of the API.")
def props():
    return json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/props.json", "r"))

@api.get("/docs/parameters", description="Get the parameters of the API.")
def parameters():
    return json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/parameters.json", "r"))

@api.get("/docs/responses", description="Get the responses of the API.")
def responses():
    return json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/responses.json", "r"))

@api.get("/getserverstructure", description="Get a server structure.")
def get_server_structure(id: int, token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    global data_token
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{id}"]
    except:
        traceback.print_exc()
        data_token = None
        pass
    if token is not None:
        print(Bot.config.DISCORD_TOKEN)
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            headers = {
                'Authorization': f'Bot {Bot.config.DISCORD_TOKEN}',
                'Content-Type': 'application/json'
            }
            response = requests.get(f'https://discord.com/api/v9/guilds/{id}/channels', headers=headers)
            if response.status_code == 200:
                channels = {}
                response_channels = response.json()
                for channel in response_channels:
                    if channel["type"] == 0 or channel["type"] == 5 or channel["type"] == 2:
                        channel_category = requests.get(f'https://discord.com/api/v9/channels/{channel["parent_id"]}', headers=headers)
                        category = None
                        try:
                            category = channel_category.json()["name"]
                        except:
                            category = None
                            pass
                        if not channels.get(category):
                            channels[category] = []
                        if channel["type"] == 0 or channel["type"] == 5:
                            channel_data = {
                                "name": channel["name"],
                                "id": channel["id"],
                                "type": "text",
                            }
                            channels[category].append(channel_data)
                        if channel["type"] == 2:
                            channel_data = {
                                "name": channel["name"],
                                "id": channel["id"],
                                "type": "voice",
                            }
                            channels[category].append(channel_data)
                return channels     
            else:
                return response.json()


@api.get("/{endpoint}", description="Get an endpoint.")
def get_endpoint(endpoint: int,
                 token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None, download: bool = False):
    global data_token
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    except:
        data_token = None
        pass
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                if download is True:
                    return fastapi.responses.FileResponse(
                        f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                        media_type='application/octet-stream', filename=f"astriod-api-{endpoint}-{token}.json")
                else:
                    return json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r"))
            except FileNotFoundError:
                return fastapi.responses.JSONResponse(status_code=404, content={
                    "message": "This endpoint does not exist."})
        else:
            return fastapi.responses.JSONResponse(status_code=401,
                                                  content={"message": "The provided token is invalid."})
    else:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})


@api.get("/bridges/{endpoint}", description="Get an endpoint.")
def get_bridges(endpoint: int,
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

                return fastapi.responses.JSONResponse(
                    {"discord": bridges_discord, "guilded": bridges_guilded, "revolt": bridges_revolt}, status_code=200)
            except FileNotFoundError:
                return fastapi.responses.JSONResponse(status_code=404,
                                                      content={"message": "This endpoint does not exist."})
        else:
            return fastapi.responses.JSONResponse(status_code=401,
                                                  content={"message": "The provided token is invalid."})
    else:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})


@api.post("/token/{endpoint}", description="Generate a new token. (Only works with astroid-Bot)")
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
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "The provided token is invalid."})

def validate_response():
    return fastapi.responses.JSONResponse(status_code=200, content={"message": "Success."})

class EndpointUpdateRequest(BaseModel):
    webhook_discord: Optional[str] = Field(None, max_length=350, min_length=50)
    webhook_guilded: Optional[str] = Field(None, max_length=350, min_length=50)
    webhook_revolt: Optional[str] = Field(None, max_length=350, min_length=50)
    log_discord: Optional[int]
    log_guilded: Optional[str] = Field(None, max_length=50, min_length=5)
    log_revolt: Optional[str] = Field(None, max_length=50, min_length=5)
    channel_discord: Optional[int]
    channel_guilded: Optional[str] = Field(None, max_length=150, min_length=5)
    channel_revolt: Optional[str] = Field(None, max_length=50, min_length=5)
    blacklist: Optional[str] = Field(None, max_length=250, min_length=1)
    sender_channel: Optional[str] = Field(None, max_length=80, min_length=10)
    trigger: Optional[bool]
    sender: Optional[str] = Field(None, max_length=10, min_length=5)
    message_author_name: Optional[str] = Field(None, max_length=50, min_length=1)
    message_author_avatar: Optional[str] = Field(None, max_length=250, min_length=50)
    allowed_ids: Optional[str] = Field(None, max_length=50, min_length=5)
    message_author_id: Optional[str] = Field(None, max_length=50, min_length=5)
    message_content: Optional[str] = Field(None, max_length=1500)
    message_attachments: Optional[str] = Field(None, max_length=1550, min_length=20)
    message_embed: Optional[str] = Field(None, max_length=1500)
    selfuse: Optional[bool]
    token: Optional[str] = Field(None, max_length=85, min_length=71)
    beta: Optional[bool] = False

async def update_json_file(endpoint: str, data: dict, field: str, value):
    if value:
        if isinstance(value, list):
            data[field] = data.get(field, []) + value
        else:
            data[field] = value

async def validate_token(endpoint: int, token: str, master_token: str, tokens_path: str):
    with open(tokens_path, "r") as file:
        tokens = json.load(file)
    data_token = tokens.get(str(endpoint))
    if token != master_token and token != data_token:
        raise HTTPException(status_code=401, detail="The provided token is invalid.")

async def load_json_file(filepath: str):
    with open(filepath, "r+") as file:
        return json.load(file), file

@api.post("/update/{endpoint}", description="Modify an endpoint.", response_description="Endpoint with updated data.")
async def post_endpoint(
    endpoint: int,
    index: int = None,
    webhook_discord: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
    webhook_guilded: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
    webhook_revolt: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
    log_discord: str = None,
    log_guilded: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    log_revolt: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    channel_discord: str = None,
    channel_guilded: Annotated[str, fastapi.Query(max_length=150, min_length=5)] = None,
    channel_revolt: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    blacklist: Annotated[str, fastapi.Query(max_length=250, min_length=1)] = None,
    sender_channel: Annotated[str, fastapi.Query(max_length=80, min_length=10)] = None,
    trigger: bool = None,
    sender: Annotated[str, fastapi.Query(max_length=10, min_length=5)] = None,
    message_author_name: Annotated[str, fastapi.Query(max_length=50, min_length=1)] = None,
    message_author_avatar: Annotated[str, fastapi.Query(max_length=250, min_length=50)] = None,
    allowed_ids: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    message_author_id: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    message_content: Annotated[str, fastapi.Query(max_length=1500)] = None,
    message_attachments: Annotated[str, fastapi.Query(max_length=1550, min_length=20)] = None,
    message_embed: Annotated[str, fastapi.Query(max_length=1500)] = None,
    selfuse: bool = None,
    token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
    beta: bool = False
):
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]

        if token is not None:
            if token == Bot.config.MASTER_TOKEN or token == data_token:
                if f"{endpoint}.json" in os.listdir(f"{pathlib.Path(__file__).parent.resolve()}/endpoints"):
                    file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+")
                    json_file = json.load(file)

                    if beta is True:
                        json_file["config"]["isbeta"] = True

                    if webhook_discord:
                        if webhook_discord in json_file["config"]["webhooks"]["discord"]:
                            return fastapi.responses.JSONResponse(status_code=200, content={"message": "This webhook already exists."})
                        elif index is not None:
                            json_file["config"]["webhooks"]["discord"][index] = webhook_discord
                        else:
                            json_file["config"]["webhooks"]["discord"].append(webhook_discord)

                    if webhook_guilded:
                        if webhook_guilded in json_file["config"]["webhooks"]["guilded"]:
                            return fastapi.responses.JSONResponse(status_code=200, content={"message": "This webhook already exists."})
                        elif index is not None:
                            json_file["config"]["webhooks"]["guilded"][index] = webhook_guilded
                        else:
                            json_file["config"]["webhooks"]["guilded"].append(webhook_guilded)

                    if webhook_revolt:
                        if webhook_revolt in json_file["config"]["webhooks"]["revolt"]:
                            return fastapi.responses.JSONResponse(status_code=200, content={"message": "This webhook already exists."})
                        elif index is not None:
                            json_file["config"]["webhooks"]["revolt"][index] = webhook_revolt
                        else:
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
                        if channel_discord in json_file["config"]["channels"]["discord"]:
                            return fastapi.responses.JSONResponse(status_code=200, content={"message": "This channel already exists."})
                        elif index is not None:
                            json_file["config"]["channels"]["discord"][index] = channel_discord
                        else:
                            json_file["config"]["channels"]["discord"].append(channel_discord)

                    if channel_guilded:
                        if channel_guilded in json_file["config"]["channels"]["guilded"]:
                            return fastapi.responses.JSONResponse(status_code=200, content={"message": "This channel already exists."})
                        elif index is not None:
                            json_file["config"]["channels"]["guilded"][index] = channel_guilded
                        else:
                            json_file["config"]["channels"]["guilded"].append(channel_guilded)

                    if channel_revolt:
                        if channel_revolt in json_file["config"]["channels"]["revolt"]:
                            return fastapi.responses.JSONResponse(status_code=200, content={"message": "This channel already exists."})
                        elif index is not None:
                            json_file["config"]["channels"]["revolt"][index] = channel_revolt
                        else:
                            json_file["config"]["channels"]["revolt"].append(channel_revolt)

                    if blacklist:
                        if "," in blacklist:
                            for val in blacklist.split(","):
                                if val.lower() not in [x.lower() for x in json_file["config"]["blacklist"]]:
                                    json_file["config"]["blacklist"].append(val.lower())
                        else:
                            if blacklist.lower() not in json_file["config"]["blacklist"]:
                                if index is not None:
                                    json_file["config"]["blacklist"][index] = blacklist.lower()
                                else:
                                    json_file["config"]["blacklist"].append(blacklist.lower())

                    if trigger:
                        json_file["meta"]["trigger"] = trigger

                    if sender_channel:
                        json_file["meta"]["sender-channel"] = sender_channel

                    if sender:
                        if sender in ["discord", "guilded", "revolt"]:
                            json_file["meta"]["sender"] = sender
                            json_file["meta"]["read"][sender] = True
                        else:
                            return fastapi.responses.JSONResponse(status_code=400, content={"message": "Invalid sender."})

                    if message_author_name:
                        json_file["meta"]["message"]["author"]["name"] = message_author_name

                    if message_author_avatar:
                        json_file["meta"]["message"]["author"]["avatar"] = message_author_avatar

                    if allowed_ids:
                        if "," in allowed_ids:
                            for val in allowed_ids.split(","):
                                if val not in json_file["config"]["allowed-ids"]:
                                    json_file["config"]["allowed-ids"].append(val)
                        else:
                            if allowed_ids not in json_file["config"]["allowed-ids"]:
                                if index is not None:
                                    json_file["config"]["allowed-ids"][index] = allowed_ids
                                else:
                                    json_file["config"]["allowed-ids"].append(allowed_ids)

                    if message_author_id:
                        json_file["meta"]["message"]["author"]["id"] = message_author_id

                    if message_content:
                        if sender == "discord":
                            if "http" in message_content or "https" in message_content:
                                urls = re.findall(r'(https?://\S+)', message_content)
                                for url in urls:
                                    image_markdown = f"![{url}]({url})"
                                    message_content = message_content.replace(url, image_markdown) + message_content.split(url)[1]
                            json_file["meta"]["message"]["content"] = message_content
                        else:
                            json_file["meta"]["message"]["content"] = message_content

                    if message_attachments:
                        if "," in message_attachments:
                            for val in message_attachments.split(","):
                                if val.lower() not in [x.lower() for x in json_file["meta"]["message"]["attachments"]]:
                                    if sender == "discord":
                                        json_file["meta"]["message"]["attachments"].append(f"![]({val})")
                                    else:
                                        json_file["meta"]["message"]["attachments"].append(val)
                        else:
                            json_file["meta"]["message"]["attachments"] = []

                    if message_embed:
                        embed_object = json.loads(message_embed.replace("'", '"'))
                        json_file["meta"]["message"]["embed"] = embed_object
                    

                    file.seek(0)
                    json.dump(json_file, file)
                    file.truncate()
                    file.close()

                    updated_json = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+"))

                    if not updated_json["config"]["self-user"] is True:
                        if updated_json["meta"]["trigger"]:
                            await send_webhook_notifications(updated_json, endpoint)
                            waiting_secs = 0
                            max_secs = 10
                            while True:
                                check_file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+")
                                check_json = json.load(check_file)
                                if (check_json["meta"]["read"]["discord"] == True
                                        and check_json["meta"]["read"]["guilded"] == True
                                        and check_json["meta"]["read"]["revolt"] == True):
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
                                    check_file.seek(0)
                                    json.dump(check_json, check_file)
                                    check_file.truncate()
                                    check_file.close()
                                    break

                        else:
                            return fastapi.responses.JSONResponse(
                                status_code=200,
                                content={"message": "This endpoint activated self-usage."},
                            )

                    return fastapi.responses.JSONResponse(status_code=200, content=json_file)
                else:
                    return fastapi.responses.JSONResponse(status_code=404, content={"message": "This endpoint does not exist."})
            else:
                return fastapi.responses.JSONResponse(status_code=401, content={"message": "The provided token is invalid."})
        else:
            return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})
    except Exception as e:
        traceback.print_exc()
        return fastapi.responses.JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})

async def send_webhook_notifications(updated_json, endpoint):
    sender = updated_json["meta"]["sender"]
    if sender == "guilded":
        await send_discord_notifications(updated_json, endpoint)
    if sender == "discord":
        await send_guilded_notifications(updated_json, endpoint)
    if sender == "revolt":
        await send_from_revolt(updated_json, endpoint)


async def send_from_revolt(updated_json, endpoint):
    discord_webhook = updated_json["config"]["webhooks"]["discord"][updated_json["config"]["channels"]["revolt"].index(updated_json["meta"]["sender-channel"])]
    async with aiohttp.ClientSession() as session:
        webhook_obj = nextcord.Webhook.from_url(discord_webhook, session=session)
        await webhook_obj.send(content=updated_json["meta"]["message"]["content"], avatar_url=updated_json["meta"]["message"]["author"]["avatar"], username=updated_json["meta"]["message"]["author"]["name"])
        await session.post(f"https://astroid.deutscher775.de/read/{endpoint}?token={Bot.config.MASTER_TOKEN}&read_discord=true")
    guilded_webhook = updated_json["config"]["webhooks"]["guilded"][updated_json["config"]["channels"]["revolt"].index(updated_json["meta"]["sender-channel"])]
    async with aiohttp.ClientSession() as session:
        webhook_obj = guilded.Webhook.from_url(guilded_webhook, session=session)
        await webhook_obj.send(content=updated_json["meta"]["message"]["content"], avatar_url=updated_json["meta"]["message"]["author"]["avatar"], username=updated_json["meta"]["message"]["author"]["name"])
        await session.post(f"https://astroid.deutscher775.de/read/{endpoint}?token={Bot.config.MASTER_TOKEN}&read_guilded=true")

async def send_discord_notifications(updated_json, endpoint):
    webhook = updated_json["config"]["webhooks"]["discord"][updated_json["config"]["channels"]["guilded"].index(updated_json["meta"]["sender-channel"])]
    async with aiohttp.ClientSession() as session:
        webhook_obj = nextcord.Webhook.from_url(webhook, session=session)
        await webhook_obj.send(content=updated_json["meta"]["message"]["content"], avatar_url=updated_json["meta"]["message"]["author"]["avatar"], username=updated_json["meta"]["message"]["author"]["name"])
        await session.post(f"https://astroid.deutscher775.de/read/{endpoint}?token={Bot.config.MASTER_TOKEN}&read_discord=true")



async def send_guilded_notifications(updated_json, endpoint):
    webhook = updated_json["config"]["webhooks"]["guilded"][updated_json["config"]["channels"]["discord"].index(updated_json["meta"]["sender-channel"])]
    async with aiohttp.ClientSession() as session:
        webhook_obj = guilded.Webhook.from_url(webhook, session=session)
        await webhook_obj.send(content=updated_json["meta"]["message"]["content"], avatar_url=updated_json["meta"]["message"]["author"]["avatar"], username=updated_json["meta"]["message"]["author"]["name"])
        await session.post(f"https://astroid.deutscher775.de/read/{endpoint}?token={Bot.config.MASTER_TOKEN}&read_guilded=true")



@api.post("/read/{endpoint}",
          description="Mark the 'meta' as read on the platform(s). "
                      "[Note: Currently only used in the astroid Revolt-bot.]")
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
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "The provided token is invalid."})


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
        return fastapi.responses.JSONResponse(status_code=201, content={"message": "Created."})
    except FileExistsError:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint exists already."})


@api.delete("/delete/{endpoint}", description="Delete an endpoint.")
def delete_endpoint(endpoint: int,
                    token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
        if token is not None:
            if token == data_token or token == Bot.config.MASTER_TOKEN:
                try:
                    os.remove(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json")
                    return fastapi.responses.JSONResponse(status_code=200, content={"message": "Deleted."})
                except FileNotFoundError:
                    return fastapi.responses.JSONResponse(status_code=404,
                                                        content={"message": "This endpoint does not exist."})
            else:
                return fastapi.responses.JSONResponse(status_code=401,
                                                    content={"message": "The provided token is invalid."})
        else:
            return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})
    except KeyError:
        if token == Bot.config.MASTER_TOKEN:
            try:
                os.remove(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json")
                return fastapi.responses.JSONResponse(status_code=200, content={"message": "Deleted."})
            except FileNotFoundError:
                return fastapi.responses.JSONResponse(status_code=404,
                                                    content={"message": "This endpoint does not exist."})
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This endpoint does not exist."})


@api.delete("/delete/data/{endpiont}", description="Edit or delete specific data of endpoint")
def delete_enpoint_data(endpoint: int,
                        webhook_discord: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        webhook_guilded: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        webhook_revolt: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        log_discord: int = None,
                        log_guilded: Annotated[str, fastapi.Query(max_length=5, min_length=50)] = None,
                        log_revolt: Annotated[str, fastapi.Query(max_length=5, min_length=50)] = None,
                        channel_discord: int = None,
                        channel_guilded: Annotated[str, fastapi.Query(max_length=150, min_length=5)] = None,
                        channel_revolt: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
                        blacklist: Annotated[str, fastapi.Query(max_length=250, min_length=1)] = None,
                        sender_channel: Annotated[str, fastapi.Query(max_length=80, min_length=10)] = None,
                        sender: Annotated[str, fastapi.Query(max_length=10, min_length=5)] = None,
                        message_author_name: Annotated[str, fastapi.Query(max_length=50, min_length=1)] = None,
                        message_author_avatar: Annotated[str, fastapi.Query(max_length=250, min_length=50)] = None,
                        allowed_ids: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
                        message_author_id: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
                        message_content: Annotated[str, fastapi.Query(max_length=1500)] = None,
                        message_attachments: Annotated[str, fastapi.Query(max_length=1550, min_length=20)] = None,
                        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                json_file = open(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+")
                json_data = json.load(json_file)
                if webhook_discord:
                    print(json_data["config"]["webhooks"]["discord"].index(webhook_discord))
                    json_data["config"]["webhooks"]["discord"][json_data["config"]["webhooks"]["discord"].index(webhook_discord)] = None
                if webhook_guilded:
                    json_data["config"]["webhooks"]["guilded"][json_data["config"]["webhooks"]["guilded"].index(webhook_guilded)] = None
                if webhook_revolt:
                    json_data["config"]["webhooks"]["revolt"][json_data["config"]["webhooks"]["revolt"].index(webhook_revolt)] = None
                if log_discord:
                    json_data["config"]["logs"]["discord"][json_data["config"]["logs"]["discord"].index(log_discord)] = None
                if log_guilded:
                    json_data["config"]["logs"]["guilded"][json_data["config"]["logs"]["guilded"].index(log_guilded)] = None
                if log_revolt:
                    json_data["config"]["logs"]["revolt"][json_data["config"]["logs"]["revolt"].index(log_revolt)] = None

                if blacklist:
                    if "," in blacklist:
                        blacklist = blacklist.split(",")
                        for word in blacklist:
                            if word in json_data["config"]["blacklist"]:
                                json_data["config"]["blacklist"].pop(word)
                    else:
                        if blacklist in json_data["config"]["blacklist"]:
                            json_data["config"]["blacklist"].pop(blacklist)

                if allowed_ids:
                    if "," in allowed_ids:
                        allowed_ids = allowed_ids.split(",")
                        for id in allowed_ids:
                            if id in json_data["config"]["allowed-ids"]:
                                json_data["config"]["allowed-ids"].pop(int(id))
                    else:
                        if allowed_ids in json_data["config"]["allowed-ids"]:
                            json_data["config"]["allowed-ids"].pop(int(allowed_ids))

                if channel_discord:
                    json_data["config"]["channels"]["discord"][json_data["config"]["config"]["discord"].index(channel_discord)] = None
                if channel_guilded:
                    json_data["config"]["channels"]["guilded"][json_data["config"]["config"]["guilded"].index(channel_guilded)] = None
                if channel_revolt:
                    json_data["config"]["channels"]["revolt"][json_data["config"]["config"]["revolt"].index(channel_revolt)] = None

                if sender_channel:
                    json_data["meta"]["sender_channel"] = None
                if sender:
                    json_data["meta"]["sender"] = None
                if message_author_name:
                    json_data["meta"]["message"]["author"]["name"] = None
                if message_author_id:
                    json_data["meta"]["message"]["author"]["id"] = None
                if message_author_avatar:
                    json_data["meta"]["message"]["author"]["avatar"] = None
                if message_content:
                    json_data["meta"]["message"]["content"] = None
                if message_attachments:
                    json_data["meta"]["message"]["attachments"].clear()

                json_file.seek(0)
                json.dump(json_data, json_file)
                json_file.truncate()
                json_file.close()

            except FileNotFoundError:
                return fastapi.responses.JSONResponse(status_code=404,
                                                      content={"message": "This endpoint does not exist."})
        else:
            return fastapi.responses.JSONResponse(status_code=401,
                                                  content={"message": "The provided token is invalid."})
    else:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})


asyncio.run(uvicorn.run(api, host="localhost", port=9921))
