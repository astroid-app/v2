import json
import os
import pathlib
import traceback
import uvicorn
import fastapi
import Bot.config
import fastapi.security
import secrets
from typing import Annotated
import astroidapi.attachment_processor
import astroidapi.endpoint_update_handler
import astroidapi.errors
import astroidapi.get_channel_information
import astroidapi.health_check
import astroidapi.read_handler
import astroidapi.surrealdb_handler
import astroidapi.statistics
import astroidapi.suspension_handler
import beta_users
from fastapi.middleware.cors import CORSMiddleware
import requests
import sentry_sdk
from PIL import Image
from fastapi import HTTPException
import slowapi
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
import astroidapi

# Configure logging to log to a file
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("_astroidapi.log", mode="a")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)



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


limiter = Limiter(key_func=get_remote_address)
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

@api.get("/viewlogs")
def view_logs(token: Annotated[str, fastapi.Query(max_length=85, min_length=10)])	:
    if token == Bot.config.LOG_TOKEN:
        with open("astroidapi.log", "r") as file:
            return fastapi.responses.PlainTextResponse(status_code=200, content=file.read())
    else:
        return fastapi.responses.Response(status_code=404)

@api.get("/ga-test")
def ga_test():
    return fastapi.responses.JSONResponse(status_code=200, content={"commited": "210824-15"})

@api.get("/assets/{asset}", description="Get an asset.")
def get_asset(asset: str, width: int = None, height: int = None):
    if not width and not height:
        try:
            return fastapi.responses.FileResponse(f"{pathlib.Path(__file__).parent.parent.resolve()}/assets/{asset}")
        except:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This asset does not exist."})
    else:
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
    return fastapi.responses.RedirectResponse(status_code=301, url="https://docs.astroid.cc")

@api.get("/", description="Home.")
def root():
    home_data = {
        "heading": "Astroid API",
        "description": "Astroid API for getting and modifying endpoints.",
        "website": "https://astroid.cc",
        "privacy": "https://astroid.cc/privacy",
        "terms": "https://astroid.cc/terms",
        "imprint": "https://deutscher775.de/imprint.html",
        "docs": "https://astroid.cc/docs",
        "discord": "https://discord.gg/DbrFADj6Xw",

    }
    return fastapi.responses.JSONResponse(status_code=200, content=home_data)


@api.get("/statistics", description="Get the statistics.")
async def get_statistics():
    return await astroidapi.statistics.get_statistics()

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

@api.get("/cdn/{assetId}", description="Get an asset from the CDN.")
async def get_cdn_asset(assetId: str):
    asset = await astroidapi.surrealdb_handler.AttachmentProcessor.get_attachment(assetId)
    try:
        if asset:
            return fastapi.responses.FileResponse(f"{pathlib.Path(__file__).parent.resolve()}/astroidapi/TMP_attachments/{assetId}.{asset['type']}")
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This asset does not exist."})
    except FileNotFoundError:
        return fastapi.responses.JSONResponse(status_code=404, content={"message": "This asset does not exist."})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})

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
        logging.exception(traceback.print_exc())
        data_token = None
        pass
    if token is not None:
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
async def get_endpoint(endpoint: int,
                 token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None, download: bool = False):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    
    global data_token
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    except:
        data_token = None
        pass
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                return fastapi.responses.JSONResponse(status_code=200, content=await astroidapi.surrealdb_handler.get_endpoint(endpoint))
            except astroidapi.errors.SurrealDBHandler.EndpointNotFoundError as e:
                return fastapi.responses.JSONResponse(status_code=404, content={"message": f"Endpoint {endpoint} not found."})
            except astroidapi.errors.SurrealDBHandler.GetEndpointError as e:
                return fastapi.responses.JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})
            except Exception as e:
                logging.exception(traceback.print_exc())
        else:
            return fastapi.responses.JSONResponse(status_code=401,
                                                  content={"message": "The provided token is invalid."})
    else:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})


@api.get("/bridges/{endpoint}", description="Get an endpoint.")
async def get_bridges(endpoint: int,
                token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    global data_token
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    except:
        data_token = None
        pass
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                bridges_json = await astroidapi.surrealdb_handler.get_endpoint(endpoint)
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
async def new_token(endpoint: int,
              master_token: Annotated[str, fastapi.Query(max_length=85, min_length=85)]):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    
    if master_token == Bot.config.MASTER_TOKEN:
        with open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r+") as tokens:
            token = secrets.token_urlsafe(53)
            data = json.load(tokens)
            data[f"{endpoint}"] = token
            tokens.seek(0)
            json.dump(data, tokens)
            tokens.truncate()
            tokens.close()
            return {f"token": token}

    else:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "The provided token is invalid."})

@api.delete("/tempattachments", description="Clear the temporary attachments.")
async def clear_temporary_attachments(master_token: Annotated[str, fastapi.Query(max_length=85, min_length=85)]):
    if master_token == Bot.config.MASTER_TOKEN:
        try:
            total_files = len(os.listdir(f"{pathlib.Path(__file__).parent.resolve()}/astroidapi/TMP_attachments")) - 1
            await astroidapi.attachment_processor.force_clear_temporary_attachments()
            requests.post("https://discord.com/api/webhooks/1279497897016299553/3GrZI75dDYwIkwYBac4o2ApJgzlVVCPIZnon_iE5RtaRIyiYUwcdaXxA327oNZyWZXs4", json={"content": f"[Astroid API - TMP Attachments] Deleted {total_files} temporary attachments."})
            return fastapi.responses.JSONResponse(status_code=200, content={"message": "Success."})
        except Exception as e:
            logging.exception(traceback.print_exc())
            requests.post("https://discord.com/api/webhooks/1279497897016299553/3GrZI75dDYwIkwYBac4o2ApJgzlVVCPIZnon_iE5RtaRIyiYUwcdaXxA327oNZyWZXs4", json={"content": f"[Astroid API - TMP Attachments] An error occurred while deleting temporary attachments:\n\n `{e}`"})
            return fastapi.responses.JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})
    else:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "The provided token is invalid."})

@api.post("/update/{endpoint}", description="Modify an endpoint.", response_description="Endpoint with updated data.")
async def post_endpoint(
    endpoint: int,
    index: int = None,
    webhook_discord: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
    webhook_guilded: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
    webhook_revolt: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
    webhook_nerimity: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
    log_discord: str = None,
    log_guilded: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    log_revolt: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    log_nerimity: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    channel_discord: str = None,
    channel_guilded: Annotated[str, fastapi.Query(max_length=150, min_length=5)] = None,
    channel_revolt: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
    channel_nerimity: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
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
    beta: bool = False,
    only_check = False,
):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    
    await astroidapi.endpoint_update_handler.UpdateHandler.update_endpoint(
        endpoint=endpoint,
        index=index,
        webhook_discord=webhook_discord,
        webhook_guilded=webhook_guilded,
        webhook_revolt=webhook_revolt,
        webhook_nerimity=webhook_nerimity,
        log_discord=log_discord,
        log_guilded=log_guilded,
        log_revolt=log_revolt,
        log_nerimity=log_nerimity,
        channel_discord=channel_discord,
        channel_guilded=channel_guilded,
        channel_revolt=channel_revolt,
        channel_nerimity=channel_nerimity,
        blacklist=blacklist,
        sender_channel=sender_channel,
        trigger=trigger,
        sender=sender,
        message_author_name=message_author_name,
        message_author_avatar=message_author_avatar,
        allowed_ids=allowed_ids,
        message_author_id=message_author_id,
        message_content=message_content,
        message_attachments=message_attachments,
        message_embed=message_embed,
        selfuse=selfuse,
        token=token,
        beta=beta,
        only_check=only_check,
    )
    return await astroidapi.surrealdb_handler.get_endpoint(endpoint)


@api.patch("/sync", description="Sync the local files with the database.")
async def sync_files(endpoint: int = None, token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    if token == Bot.config.MASTER_TOKEN:
        if endpoint:
            await astroidapi.surrealdb_handler.sync_local_files(f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", True)
        else:
            await astroidapi.surrealdb_handler.sync_local_files(f"{pathlib.Path(__file__).parent.resolve()}/endpoints")
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Success."})
    else:
        return fastapi.responses.JSONResponse(status_code=404, content={"detail": "Not found"})


@api.post("/read/{endpoint}",
          description="Mark the 'meta' as read on the platform(s). "
                      "[Note: Currently only used in the astroid Revolt-bot.]")
async def mark_read(endpoint: int,
              token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
              read_discord: bool = None,
              read_guilded: bool = None,
              read_revolt: bool = None,
              read_nerimity: bool = None):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    
    if token == data_token or token == Bot.config.MASTER_TOKEN:
        try:
            if read_discord:
                await astroidapi.read_handler.ReadHandler.mark_read(endpoint, "discord")
            if read_guilded:
                await astroidapi.read_handler.ReadHandler.mark_read(endpoint, "guilded")
            if read_revolt:
                await astroidapi.read_handler.ReadHandler.mark_read(endpoint, "revolt")
            if read_nerimity:
                await astroidapi.read_handler.ReadHandler.mark_read(endpoint, "nerimity")
        except Exception as e:
            logging.exception(traceback.print_exc())
            return fastapi.responses.JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Success."})
    
    else:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "The provided token is invalid."})


@api.get("/healthcheck/{endpoint}", description="Validate the endpoints strucuture.")
async def endpoint_healthcheck(endpoint: int, token: str):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    
    if token == Bot.config.MASTER_TOKEN:
        try:
            healty = await astroidapi.health_check.HealthCheck.EndpointCheck.check(endpoint)
            if healty:
                return fastapi.responses.JSONResponse(status_code=200, content={"message": "This endpoint is healthy.", "details": None})
        except astroidapi.errors.HealtCheckError.EndpointCheckError.EndpointConfigError as e:
            return fastapi.responses.JSONResponse(status_code=500, content={"message": f"There seems to be an error in the endpoint configuration: {e}",
                                                                            "details": "configerror"})
        except astroidapi.errors.HealtCheckError.EndpointCheckError.EndpointMetaDataError as e:
            return fastapi.responses.JSONResponse(status_code=500, content={"message": f"There seems to be an error in the endpoint meta data: {e}",
                                                                            "details": "metadataerror"})
        except astroidapi.errors.HealtCheckError.EndpointCheckError as e:
            return fastapi.responses.JSONResponse(status_code=500, content={"message": f"An error occurred: {e}",
                                                                            "details": "unexpectederror"})
        except astroidapi.errors.SurrealDBHandler.EndpointNotFoundError:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This endpoint does not exist.",
                                                                            "details": "notfound"})
        except astroidapi.errors.SurrealDBHandler.GetEndpointError as e:
            traceback.print_exc()
            return fastapi.responses.JSONResponse(status_code=404, content={"message": f"An error occurred: {e}",
                                                                            "details": "getendpointerror"})


@api.post("/create", description="Create an endpoint.",
          response_description="Endpoints data.")
async def create_endpoint(endpoint: int):
    try:
        suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
        if suspend_status:
            return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    except:
        pass
    try:
        data = {
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
        await astroidapi.surrealdb_handler.create(endpoint, data)
        return fastapi.responses.JSONResponse(status_code=201, content={"message": "Created."})
    except FileExistsError:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint exists already."})


@api.delete("/delete/{endpoint}", description="Delete an endpoint.")
async def delete_endpoint(endpoint: int,
                    token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    try:
        data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
        if token is not None:
            if token == data_token or token == Bot.config.MASTER_TOKEN:
                try:
                    await astroidapi.surrealdb_handler.delete(endpoint)
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


@api.delete("/delete/data/{endpoint}", description="Edit or delete specific data of endpoint")
async def delete_enpoint_data(endpoint: int,
                        webhook_discord: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        webhook_guilded: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        webhook_revolt: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        webhook_nerimity: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
                        log_discord: bool = None,
                        log_guilded: bool = None,
                        log_revolt: bool = None,
                        log_nerimity: bool = None,
                        channel_discord: int = None,
                        channel_guilded: Annotated[str, fastapi.Query(max_length=150, min_length=5)] = None,
                        channel_revolt: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
                        channel_nerimity: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
                        blacklist: Annotated[str, fastapi.Query(max_length=250, min_length=1)] = None,
                        sender_channel: bool = None,
                        sender: bool = None,
                        message_author_name: bool = None,
                        message_author_avatar: bool = None,
                        allowed_ids: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
                        message_author_id: bool = None,
                        message_content: bool = None,
                        message_attachments: Annotated[str, fastapi.Query(max_length=1550, min_length=20)] = None,
                        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    
    data_token = json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r"))[f"{endpoint}"]
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                json_data = await astroidapi.surrealdb_handler.get_endpoint(endpoint)
                if webhook_discord:
                    json_data["config"]["webhooks"]["discord"].pop(json_data["config"]["webhooks"]["discord"].index(webhook_discord))
                if webhook_guilded:
                    json_data["config"]["webhooks"]["guilded"].pop(json_data["config"]["webhooks"]["guilded"].index(webhook_guilded))
                if webhook_revolt:
                    json_data["config"]["webhooks"]["revolt"].pop(json_data["config"]["webhooks"]["revolt"].index(webhook_revolt))
                if webhook_nerimity:
                    json_data["config"]["webhooks"]["nerimity"].pop(json_data["config"]["webhooks"]["nerimity"].index(webhook_nerimity))
                
                if log_discord:
                    json_data["config"]["logs"]["discord"][json_data["config"]["logs"]["discord"]] = None
                if log_guilded:
                    json_data["config"]["logs"]["guilded"][json_data["config"]["logs"]["guilded"]] = None
                if log_revolt:
                    json_data["config"]["logs"]["revolt"][json_data["config"]["logs"]["revolt"]] = None
                if log_nerimity:
                    json_data["config"]["logs"]["nerimity"][json_data["config"]["logs"]["nerimity"]] = None

                if blacklist:
                    if "," in blacklist:
                        blacklist = blacklist.split(",")
                        for word in blacklist:
                            if word in json_data["config"]["blacklist"]:
                                json_data["config"]["blacklist"].pop(json_data["config"]["blacklist"].index(word))
                    else:
                        if blacklist in json_data["config"]["blacklist"]:
                            json_data["config"]["blacklist"].pop(json_data["config"]["blacklist"].index(blacklist))

                if allowed_ids:
                    if "," in allowed_ids:
                        allowed_ids = allowed_ids.split(",")
                        for id in allowed_ids:
                            if id in json_data["config"]["allowed-ids"]:
                                json_data["config"]["allowed-ids"].pop(json_data["config"]["allowed-ids"].index(id))
                    else:
                        if allowed_ids in json_data["config"]["allowed-ids"]:
                            json_data["config"]["allowed-ids"].pop(json_data["config"]["allowed-ids"].index(allowed_ids))

                if channel_discord:
                    json_data["config"]["channels"]["discord"].pop(json_data["config"]["channels"]["discord"].index(str(channel_discord)))
                if channel_guilded:
                    json_data["config"]["channels"]["guilded"].pop(json_data["config"]["channels"]["guilded"].index(channel_guilded))
                if channel_revolt:
                    json_data["config"]["channels"]["revolt"].pop(json_data["config"]["channels"]["revolt"].index(channel_revolt))
                if channel_nerimity:
                    json_data["config"]["channels"]["nerimity"].pop(json_data["config"]["channels"]["nerimity"].index(str(channel_nerimity)))

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
                    json_data["meta"]["message"]["attachments"].pop(json_data["meta"]["message"]["attachments"].index(message_attachments))

                data = await astroidapi.surrealdb_handler.update(endpoint, json_data)
                return fastapi.responses.JSONResponse(status_code=200, content=data)
            except astroidapi.errors.SurrealDBHandler.EndpointNotFoundError as e:
                return fastapi.responses.JSONResponse(status_code=404,
                                                      content={"message": "This endpoint does not exist."})
        else:
            return fastapi.responses.JSONResponse(status_code=401,
                                                  content={"message": "The provided token is invalid."})
    else:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "You must provide a token."})
    

@api.get("/getendpoint/{platform}", description="Get an endpoint via a platform server id.")
async def get_endpoint_platform(platform: str, id: str, token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})

    if not token == Bot.config.MASTER_TOKEN:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "The provided token is invalid. (Only the master token can be used to view or create relations.)"})
    try:
        if platform == "guilded":
            return await astroidapi.surrealdb_handler.GetEndpoint.from_guilded_id(id)
        elif platform == "revolt":
            return await astroidapi.surrealdb_handler.GetEndpoint.from_revolt_id(id)
        elif platform == "nerimity":
            return await astroidapi.surrealdb_handler.GetEndpoint.from_nerimity_id(id)
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This platform does not exist."})
    except:
        return fastapi.responses.JSONResponse(status_code=404, content={"message": "This endpoint does not exist."})


@api.post("/createendpoint/{platform}", description="Create an endpoint via a platform server id.")
async def create_endpoint_platform(platform: str, endpoint: int, id: str, token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    suspend_status = await astroidapi.suspension_handler.Endpoint.is_suspended(endpoint)
    if suspend_status:
        return fastapi.responses.JSONResponse(status_code=403, content={"message": "This endpoint is suspended."})
    
    if not token == Bot.config.MASTER_TOKEN:
        return fastapi.responses.JSONResponse(status_code=401, content={"message": "The provided token is invalid. (Only the master token can be used to view or create relations.)"})
    try:
        if platform == "guilded":
            return await astroidapi.surrealdb_handler.CreateEndpoint.for_guilded(endpoint, id)
        elif platform == "revolt":
            return await astroidapi.surrealdb_handler.CreateEndpoint.for_revolt(endpoint, id)
        elif platform == "nerimity":
            return await astroidapi.surrealdb_handler.CreateEndpoint.for_nerimity(endpoint, id)
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This platform does not exist."})
    except:
        return fastapi.responses.JSONResponse(status_code=404, content={"message": "This endpoint does not exist."})


@api.patch("/syncserverrelations", description="Sync the server relations.")
async def syncserverrelaions():
    try:
        await astroidapi.surrealdb_handler.sync_server_relations()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Success."})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})


@api.get("/channel/name/{platform}", description="Get the channel name.")
async def get_channel_name(platform: str, id: str, token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None):
    try:
        if platform == "discord":
            return await astroidapi.get_channel_information.GetChannelName.from_discord_id(int(id))
        elif platform == "guilded":
            return await astroidapi.get_channel_information.GetChannelName.from_guilded_id(id)
        elif platform == "revolt":
            return await astroidapi.get_channel_information.GetChannelName.from_revolt_id(id)
        elif platform == "nerimity":
            return await astroidapi.get_channel_information.GetChannelName.from_nerimity_id(int(id))
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"message": "This platform does not exist."})
    except:
        return fastapi.responses.JSONResponse(status_code=404, content={"message": "This channel does not exist."})



logging.info("[CORE] API started.")

uvicorn.run(api, host="localhost", port=9921)