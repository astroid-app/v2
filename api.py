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
import re
import beta_users

# import sentry_sdk

# sentry_sdk.init(
# dsn="https://ff068488c0691a55892df1b559321143@o4506933768814592.ingest.us.sentry.io/4507045108318208",
# Set traces_sample_rate to 1.0 to capture 100%
# of transactions for performance monitoring.
#  traces_sample_rate=1.0,
# Set profiles_sample_rate to 1.0 to profile 100%
# of sampled transactions.
# We recommend adjusting this value in production.
#  profiles_sample_rate=1.0,
# )

api = fastapi.FastAPI(
    title="Astroid API",
    description="Astroid API for getting and modifying endpoints.",
    version="2.1.4",
)


@api.get(
    "/",
    description="Does nothing. Just sitting there and waiting for requess. (Redirects on 'GET' to the "
                "documentation.)",
)
def root():
    return fastapi.responses.RedirectResponse(
        status_code=301, url="https://astroid.deutscher775.de/docs"
    )


@api.get("/invite/{platform}", description="Get the invite link for the astroid bot.")
def invite(platform: str, token: Annotated[str, fastapi.Query(max_length=85)] = None):
    if platform == "discord":
        return fastapi.responses.RedirectResponse(
            status_code=301,
            url="https://discord.com/oauth2/authorize?client_id=1046057269202268303&permissions=2687625280&scope=bot%20applications.commands",
        )
    elif platform == "guilded":
        return fastapi.responses.RedirectResponse(
            status_code=301,
            url="https://www.guilded.gg/b/00c19caa-e176-45f6-b1f6-7bee5ba73db9",
        )
    elif platform == "discord-beta" and token in beta_users.TOKENS:
        return fastapi.responses.RedirectResponse(
            status_code=301,
            url="https://discord.com/oauth2/authorize?client_id=1230579871059804280&permissions=138046467089&scope=applications.commands+bot",
        )
    elif platform == "guilded-beta" and token in beta_users.TOKENS:
        return fastapi.responses.RedirectResponse(
            status_code=301,
            url="https://www.guilded.gg/b/3f887186-82d5-4fe1-abbd-045748b125b3",
        )
    else:
        return fastapi.responses.JSONResponse(
            status_code=400, content={"message": "Invalid platform."}
        )

@api.get("/discord", description="Privacy")
def privacy():
    return fastapi.responses.RedirectResponse(
        status_code=301,
        url="https://discord.gg/DbrFADj6Xw"
    )


@api.get("/privacy", description="Privacy")
def privacy():
    return fastapi.responses.FileResponse(
        f"{pathlib.Path(__file__).parent.resolve()}/website/privacy.html"
    )


@api.get("/terms", description="Terms of service")
def terms():
    return fastapi.responses.FileResponse(
        f"{pathlib.Path(__file__).parent.resolve()}/website/terms.html"
    )


@api.get(
    "/{endpoint}",
    description="Get an endpoint.",
    responses={
        200: {
            "description": "Success",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "json",
                        "example": {
                            "config": {
                                "self-user": False,
                                "webhooks": {
                                    "discord": [],
                                    "guilded": [],
                                    "revolt": [],
                                },
                                "channels": {
                                    "discord": [],
                                    "guilded": [],
                                    "revolt": [],
                                },
                                "logs": {
                                    "discord": None,
                                    "guilded": None,
                                    "revolt": None,
                                },
                                "blacklist": [],
                                "allowed-ids": [],
                                "isbeta": False,
                            },
                            "meta": {
                                "sender-channel": None,
                                "trigger": False,
                                "sender": None,
                                "read": {
                                    "discord": False,
                                    "guilded": False,
                                    "revolt": False,
                                },
                                "message": {
                                    "author": {
                                        "name": None,
                                        "avatar": None,
                                        "id": None,
                                    },
                                    "content": None,
                                    "attachments": [],
                                },
                            },
                        },
                    },
                }
            },
        },
        401: {"description": "Unauthorized", "content": {"application/json": {}}},
        404: {"description": "Not Found", "content": {"application/json": {}}},
    },
)
def get_endpoint(
        endpoint: int,
        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
        download: bool = False,
):
    global data_token
    try:
        data_token = json.load(
            open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r")
        )[f"{endpoint}"]
    except:
        data_token = None
        pass
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                if download is True:
                    return fastapi.responses.FileResponse(
                        f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                        media_type="application/octet-stream",
                        filename=f"astriod-api-{endpoint}-{token}.json",
                    )
                else:
                    return json.load(
                        open(
                            f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                            "r",
                        )
                    )
            except FileNotFoundError:
                return fastapi.responses.JSONResponse(
                    status_code=404,
                    content={"message": "This endpoint does not exist."},
                )
        else:
            return fastapi.responses.JSONResponse(
                status_code=401, content={"message": "The provided token is invalid."}
            )
    else:
        return fastapi.responses.JSONResponse(
            status_code=401, content={"message": "You must provide a token."}
        )


@api.get(
    "/bridges/{endpoint}",
    description="Get an endpoint.",
    responses={
        200: {"description": "Success", "content": {"application/json": {}}},
        401: {"description": "Unauthorized", "content": {"application/json": {}}},
        404: {"description": "Not Found", "content": {"application/json": {}}},
    },
)
def get_bridges(
        endpoint: int,
        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
):
    global data_token
    try:
        data_token = json.load(
            open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r")
        )[f"{endpoint}"]
    except:
        data_token = None
        pass
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                bridges_json = json.load(
                    open(
                        f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                        "r",
                    )
                )
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
                    {
                        "discord": bridges_discord,
                        "guilded": bridges_guilded,
                        "revolt": bridges_revolt,
                    },
                    status_code=200,
                )
            except FileNotFoundError:
                return fastapi.responses.JSONResponse(
                    status_code=404,
                    content={"message": "This endpoint does not exist."},
                )
        else:
            return fastapi.responses.JSONResponse(
                status_code=401, content={"message": "The provided token is invalid."}
            )
    else:
        return fastapi.responses.JSONResponse(
            status_code=401, content={"message": "You must provide a token."}
        )


@api.post(
    "/token/{endpoint}",
    description="Generate a new token. (Only works with astroid-Bot)",
    responses={
        200: {"description": "Success", "content": {"application/json": {}}},
        403: {"description": "Forbidden", "content": {"application/json": {}}},
    },
)
def new_token(
        endpoint: int,
        master_token: Annotated[str, fastapi.Query(max_length=85, min_length=85)],
):
    if master_token == Bot.config.MASTER_TOKEN:
        with open(
                f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r+"
        ) as tokens:
            token = secrets.token_urlsafe(53)
            print(token)
            data = json.load(tokens)
            data[f"{endpoint}"] = token
            tokens.seek(0)
            json.dump(data, tokens)
            tokens.truncate()
            tokens.close()
            return {"token": token}

    else:
        return fastapi.responses.JSONResponse(
            status_code=403, content={"message": "The provided token is invalid."}
        )


@api.post(
    "/update/{endpoint}",
    description="Modify an endpoint.",
    response_description="Endpoint with updated data.",
    responses={
        200: {"description": "Success"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal Server Error"},
    },
)
async def post_endpoint(
        endpoint: int,
        index: int = None,
        webhook_discord: Annotated[
            str, fastapi.Query(max_length=350, min_length=50)
        ] = None,
        webhook_guilded: Annotated[
            str, fastapi.Query(max_length=350, min_length=50)
        ] = None,
        webhook_revolt: Annotated[str, fastapi.Query(max_length=350, min_length=50)] = None,
        log_discord: int = None,
        log_guilded: Annotated[str, fastapi.Query(max_length=5, min_length=50)] = None,
        log_revolt: Annotated[str, fastapi.Query(max_length=5, min_length=50)] = None,
        channel_discord: int = None,
        channel_guilded: Annotated[str, fastapi.Query(max_length=150, min_length=5)] = None,
        channel_revolt: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
        blacklist: Annotated[str, fastapi.Query(max_length=250, min_length=1)] = None,
        sender_channel: Annotated[str, fastapi.Query(max_length=80, min_length=10)] = None,
        trigger: bool = None,
        sender: Annotated[str, fastapi.Query(max_length=10, min_length=5)] = None,
        message_author_name: Annotated[
            str, fastapi.Query(max_length=50, min_length=1)
        ] = None,
        message_author_avatar: Annotated[
            str, fastapi.Query(max_length=250, min_length=50)
        ] = None,
        allowed_ids: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
        message_author_id: Annotated[
            str, fastapi.Query(max_length=50, min_length=5)
        ] = None,
        message_content: Annotated[str, fastapi.Query(max_length=1500)] = None,
        message_attachments: Annotated[
            str, fastapi.Query(max_length=1550, min_length=20)
        ] = None,
        message_embed: Annotated[str, fastapi.Query(max_length=1500)] = None,
        selfuse: bool = None,
        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
        beta: bool = False,
):
    try:
        data_token = json.load(
            open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r")
        )[f"{endpoint}"]
        if token is not None:
            if token == Bot.config.MASTER_TOKEN or token == data_token:
                if f"{endpoint}.json" in os.listdir(
                        f"{pathlib.Path(__file__).parent.resolve()}/endpoints"
                ):
                    file = open(
                        f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                        "r+",
                    )
                    json_file = json.load(file)
                    json_file["meta"]["read"]["revolt"] = True
                    if beta is True:
                        json_file["config"]["isbeta"] = True
                    if webhook_discord:
                        if (
                                webhook_discord
                                in json_file["config"]["webhooks"]["discord"]
                        ):
                            return fastapi.responses.JSONResponse(status_code=200)
                        elif index:
                            json_file["config"]["webhooks"]["discord"][index] = (
                                webhook_discord
                            )
                        else:
                            json_file["config"]["webhooks"]["discord"].append(
                                webhook_discord
                            )
                    if webhook_guilded:
                        if (
                                webhook_guilded
                                in json_file["config"]["webhooks"]["guilded"]
                        ):
                            return fastapi.responses.JSONResponse(status_code=200)
                        elif index:
                            json_file["config"]["webhooks"]["guilded"][index] = (
                                webhook_guilded
                            )
                        else:
                            json_file["config"]["webhooks"]["guilded"].append(
                                webhook_guilded
                            )
                    if webhook_revolt:
                        if webhook_revolt in json_file["config"]["webhooks"]["revolt"]:
                            return fastapi.responses.JSONResponse(status_code=200)
                        elif index:
                            json_file["config"]["webhooks"]["revolt"][index] = (
                                webhook_revolt
                            )
                        else:
                            json_file["config"]["webhooks"]["revolt"].append(
                                webhook_revolt
                            )
                    if selfuse is True or selfuse is False:
                        json_file["config"]["self-user"] = selfuse
                    if log_discord:
                        json_file["config"]["logs"]["discord"] = log_discord
                    if log_guilded:
                        json_file["config"]["logs"]["guilded"] = log_guilded
                    if log_revolt:
                        json_file["config"]["logs"]["revolt"] = log_revolt
                    if channel_discord:
                        if (
                                channel_discord
                                in json_file["config"]["channels"]["discord"]
                        ):
                            return fastapi.responses.JSONResponse(status_code=200)
                        elif index:
                            json_file["config"]["channels"]["discord"][index] = (
                                channel_discord
                            )
                        else:
                            json_file["config"]["channels"]["discord"].append(
                                channel_discord
                            )
                    if channel_guilded:
                        if (
                                channel_guilded
                                in json_file["config"]["channels"]["guilded"]
                        ):
                            return fastapi.responses.JSONResponse(status_code=200)
                        elif index:
                            json_file["config"]["channels"]["guilded"][index] = (
                                channel_guilded
                            )
                        else:
                            json_file["config"]["channels"]["guilded"].append(
                                channel_guilded
                            )

                    if channel_revolt:
                        if channel_revolt in json_file["config"]["channels"]["revolt"]:
                            return fastapi.responses.JSONResponse(status_code=200)
                        elif index:
                            json_file["config"]["channels"]["revolt"][index] = (
                                channel_revolt
                            )
                        else:
                            json_file["config"]["channels"]["revolt"].append(
                                channel_revolt
                            )

                    if blacklist:
                        if "," in blacklist:
                            for val in blacklist.split(","):
                                for in_value in json_file["config"]["blacklist"]:
                                    if val.lower() == in_value.lower():
                                        return fastapi.responses.JSONResponse(
                                            status_code=200
                                        )
                                else:
                                    json_file["config"]["blacklist"].append(val.lower())
                        else:
                            if blacklist.lower() in json_file["config"]["blacklist"]:
                                return fastapi.responses.JSONResponse(status_code=200)
                            else:
                                if index:
                                    json_file["config"]["blacklist"][index] = (
                                        blacklist.lower()
                                    )

                    if trigger:
                        json_file["meta"]["trigger"] = trigger
                    if sender_channel:
                        json_file["meta"]["sender-channel"] = sender_channel
                    if sender:
                        if (
                                sender == "discord"
                                or sender == "guilded"
                                or sender == "revolt"
                        ):
                            json_file["meta"]["sender"] = sender
                        else:
                            return fastapi.responses.JSONResponse(status_code=400)
                    if message_author_name:
                        json_file["meta"]["message"]["author"]["name"] = (
                            message_author_name
                        )
                    if message_author_avatar:
                        json_file["meta"]["message"]["author"]["avatar"] = (
                            message_author_avatar
                        )
                    if allowed_ids:
                        if "," in allowed_ids:
                            for val in allowed_ids.split(","):
                                if val in json_file["config"]["allowed-ids"]:
                                    return fastapi.responses.JSONResponse(
                                        status_code=200
                                    )
                                else:
                                    try:
                                        json_file["config"]["allowed-ids"].append(
                                            int(val)
                                        )
                                    except ValueError:
                                        json_file["config"]["allowed-ids"].append(val)
                        else:
                            if allowed_ids in json_file["config"]["allowed-ids"]:
                                return fastapi.responses.JSONResponse(status_code=200)
                            elif index:
                                try:
                                    json_file["config"]["allowed-ids"][index] = int(
                                        allowed_ids
                                    )
                                except ValueError:
                                    json_file["config"]["allowed-ids"][index] = (
                                        allowed_ids
                                    )
                            else:
                                try:
                                    json_file["config"]["allowed-ids"].append(
                                        int(allowed_ids)
                                    )
                                except ValueError:
                                    json_file["config"]["allowed-ids"].append(
                                        allowed_ids
                                    )
                    if message_author_id:
                        json_file["meta"]["message"]["author"]["id"] = message_author_id
                    if message_content:
                        if sender == "discord":
                            if "http" in message_content or "https" in message_content:
                                urls = re.findall(r"(https?://\S+)", message_content)
                                for url in urls:
                                    image_markdown = f"![{url}]({url})"
                                    message_content = (
                                            message_content.replace(url, image_markdown)
                                            + message_content.split(url)[1]
                                    )
                            else:
                                json_file["meta"]["message"]["content"] = (
                                    message_content
                                )
                        elif sender == "guilded":
                            json_file["meta"]["message"]["content"] = message_content
                        else:
                            json_file["meta"]["message"]["content"] = message_content
                    if message_attachments:
                        if "," in message_attachments:
                            for val in message_attachments.split(","):
                                for in_value in json_file["meta"]["message"][
                                    "attachments"
                                ]:
                                    if val.lower() == in_value.lower():
                                        return fastapi.responses.Response(
                                            status_code=200
                                        )
                                else:
                                    if sender == "discord":
                                        json_file["meta"]["message"][
                                            "attachments"
                                        ].append(f"![]({val})")
                                    else:
                                        json_file["meta"]["message"][
                                            "attachments"
                                        ].append(val)
                        else:
                            for attachment in (
                                    json_file["meta"]["message"]["attachments"]
                                    and sender == "guilded"
                            ):
                                json_file["meta"]["message"]["content"] = (
                                    attachment.replace(attachment, "")
                                )

                    if message_embed:
                        if (
                                "http" not in message_content
                                and "https" not in message_content
                        ):
                            embed_object = json.loads(message_embed.replace("'", '"'))
                            json_file["meta"]["message"]["embed"] = embed_object

                    file.seek(0)
                    json.dump(json_file, file)
                    file.truncate()
                    file.close()

                    updated_file = open(
                        f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                        "r+",
                    )
                    updated_json = json.load(updated_file)
                    try:
                        gc_embed = updated_json["meta"]["message"]["embed"]
                    except KeyError:
                        updated_json["meta"]["message"]["embed"] = None
                    if updated_json["config"]["self-user"] is False:
                        sender = updated_json["meta"]["sender"]
                        if sender == "discord":
                            session = aiohttp.ClientSession()
                            updated_json["meta"]["read"]["discord"] = True
                            global webhook_url_g
                            if not updated_json["config"]["channels"]["guilded"]:
                                updated_json["meta"]["read"]["guilded"] = True
                            else:
                                for channel in updated_json["config"]["channels"][
                                    "discord"
                                ]:
                                    if (
                                            str(channel)
                                            == updated_json["meta"]["sender-channel"]
                                    ):
                                        webhook_url_g = updated_json["config"][
                                            "webhooks"
                                        ]["guilded"][
                                            updated_json["config"]["channels"][
                                                "discord"
                                            ].index(int(channel))
                                        ]
                                        if message_content or message_embed:
                                            if message_embed:
                                                gc_embed = updated_json["meta"][
                                                    "message"
                                                ]["embed"]
                                                embed = guilded.Embed(
                                                    title=gc_embed["title"],
                                                    description=gc_embed["title"],
                                                )
                                                if len(gc_embed["fields"]) != 0:
                                                    for field in gc_embed["fields"]:
                                                        embed.add_field(
                                                            name=field["name"],
                                                            value=field["value"],
                                                            inline=field["inline"],
                                                        )
                                                if gc_embed["image"]:
                                                    embed.set_image(
                                                        url=gc_embed["image"]
                                                    )
                                                if gc_embed["thumbnail"]:
                                                    embed.set_thumbnail(
                                                        url=gc_embed["thumbnail"]
                                                    )
                                                if gc_embed["footer"]:
                                                    embed.set_footer(
                                                        text=gc_embed["footer"]
                                                    )
                                                await guilded.Webhook.from_url(
                                                    webhook_url_g, session=session
                                                ).send(
                                                    content=updated_json["meta"][
                                                        "message"
                                                    ]["content"],
                                                    avatar_url=updated_json["meta"][
                                                        "message"
                                                    ]["author"]["avatar"],
                                                    username=updated_json["meta"][
                                                        "message"
                                                    ]["author"]["name"],
                                                    embed=embed,
                                                )
                                            else:
                                                await guilded.Webhook.from_url(
                                                    webhook_url_g, session=session
                                                ).send(
                                                    content=updated_json["meta"][
                                                        "message"
                                                    ]["content"],
                                                    avatar_url=updated_json["meta"][
                                                        "message"
                                                    ]["author"]["avatar"],
                                                    username=updated_json["meta"][
                                                        "message"
                                                    ]["author"]["name"],
                                                )
                                        if updated_json["meta"]["message"][
                                            "attachments"
                                        ]:
                                            for attachment in updated_json["meta"][
                                                "message"
                                            ]["attachments"]:
                                                await guilded.Webhook.from_url(
                                                    webhook_url_g, session=session
                                                ).send(
                                                    content=attachment,
                                                    avatar_url=updated_json["meta"][
                                                        "message"
                                                    ]["author"]["avatar"],
                                                    username=updated_json["meta"][
                                                        "message"
                                                    ]["author"]["name"],
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
                            if not updated_json["config"]["channels"]["discord"]:
                                updated_json["meta"]["read"]["discord"] = True
                            else:
                                for channel in updated_json["config"]["channels"][
                                    "guilded"
                                ]:
                                    if (
                                            str(channel)
                                            == updated_json["meta"]["sender-channel"]
                                    ):
                                        webhook_url_d = updated_json["config"][
                                            "webhooks"
                                        ]["discord"][
                                            updated_json["config"]["channels"][
                                                "guilded"
                                            ].index(str(channel))
                                        ]
                                        if message_content or message_embed:
                                            if message_embed:
                                                gc_embed = updated_json["meta"][
                                                    "message"
                                                ]["embed"]
                                                embed = nextcord.Embed(
                                                    title=gc_embed["title"],
                                                    description=gc_embed["title"],
                                                )
                                                if len(gc_embed["fields"]) != 0:
                                                    for field in gc_embed["fields"]:
                                                        embed.add_field(
                                                            name=field["name"],
                                                            value=field["value"],
                                                            inline=field["inline"],
                                                        )
                                                if gc_embed["image"]:
                                                    print(
                                                        gc_embed["image"].replace(
                                                            "!PARAM", "&"
                                                        )
                                                    )
                                                    embed.set_image(
                                                        url=gc_embed["image"]
                                                        .replace("!PARAM", "&")
                                                        .split("?")[0]
                                                        .replace("?", "")
                                                    )
                                                if gc_embed["thumbnail"]:
                                                    print(
                                                        gc_embed["thumbnail"].replace("!PARAM", "&")
                                                    )
                                                    embed.set_thumbnail(
                                                        url=gc_embed["thumbnail"].replace("!PARAM", "&")
                                                    )
                                                if gc_embed["footer"]:
                                                    embed.set_footer(text=gc_embed["footer"])
                                                await nextcord.Webhook.from_url(
                                                    webhook_url_d, session=session
                                                ).send(
                                                    content=updated_json["meta"]["message"]["content"],
                                                    avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                                    username=updated_json["meta"]["message"]["author"]["name"],
                                                    embed=embed,
                                                )
                                            else:
                                                await nextcord.Webhook.from_url(
                                                    webhook_url_d, session=session
                                                ).send(
                                                    content=updated_json["meta"]["message"]["content"],
                                                    avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                                    username=updated_json["meta"]["message"]["author"]["name"],
                                                )
                                        if updated_json["meta"]["message"]["attachments"]:
                                            await nextcord.Webhook.from_url(
                                                webhook_url_d, session=session
                                            ).send(
                                                content=f"![]({attachment})",
                                                avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                                username=updated_json["meta"]["message"]["author"]["name"],
                                                files=[updated_json["meta"]["message"]["attachments"]]

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
                            if not updated_json["config"]["channels"]["discord"]:
                                updated_json["meta"]["read"]["discord"] = True
                            elif (
                                    str(updated_json["meta"]["sender-channel"])
                                    in updated_json["config"]["channels"]["revolt"]
                            ):
                                discord_webhook_url = updated_json["config"][
                                    "webhooks"
                                ]["discord"][
                                    updated_json["config"]["channels"]["revolt"].index(
                                        str(updated_json["meta"]["sender-channel"])
                                    )
                                ]
                                print(discord_webhook_url)
                                if message_content:
                                    await nextcord.Webhook.from_url(
                                        discord_webhook_url, session=session
                                    ).send(
                                        content=updated_json["meta"]["message"]["content"],
                                        avatar_url=updated_json["meta"]["message"][ "author"]["avatar"],
                                        username=updated_json["meta"]["message"]["author"]["name"],
                                    )
                                if updated_json["meta"]["message"]["attachments"]:
                                    for attachment in updated_json["meta"]["message"]["attachments"]:
                                        await nextcord.Webhook.from_url(
                                            discord_webhook_url, session=session
                                        ).send(
                                            content=attachment,
                                            avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                            username=updated_json["meta"]["message"]["author"]["name"],
                                        )
                                updated_json["meta"]["read"]["discord"] = True
                            global guilded_webhook_url
                            if not updated_json["config"]["channels"]["guilded"]:
                                updated_json["meta"]["read"]["guilded"] = True
                            elif str(updated_json["meta"]["sender-channel"]) in str(
                                    updated_json["config"]["channels"]["revolt"]
                            ):
                                guilded_webhook_url = updated_json["config"][
                                    "webhooks"
                                ]["guilded"][
                                    updated_json["config"]["channels"]["revolt"].index(
                                        str(updated_json["meta"]["sender-channel"])
                                    )
                                ]
                                if message_content:
                                    await guilded.Webhook.from_url(
                                        guilded_webhook_url, session=session
                                    ).send(
                                        content=updated_json["meta"]["message"]["content" ],
                                        avatar_url=updated_json["meta"]["message"]["author"]["avatar"],
                                        username=updated_json["meta"]["message"]["author"]["name"],
                                    )
                                if updated_json["meta"]["message"]["attachments"]:
                                    for attachment in updated_json["meta"]["message"][
                                        "attachments"
                                    ]:
                                        await guilded.Webhook.from_url(
                                            guilded_webhook_url, session=session
                                        ).send(
                                            content=f"![]({attachment})",
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
                            check_file = open(
                                f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                                "r+",
                            )
                            check_json = json.load(check_file)
                            if (
                                    check_json["meta"]["read"]["discord"] == True
                                    and check_json["meta"]["read"]["guilded"] == True
                                    and check_json["meta"]["read"]["revolt"] == True
                            ):
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
                        return fastapi.responses.JSONResponse(
                            status_code=200,
                            content={"message": "This endpoint activated self-usage."},
                        )
            else:
                return fastapi.responses.JSONResponse(
                    status_code=401,
                    content={"message": "The provided token is invalid."},
                )
        else:
            return fastapi.responses.JSONResponse(
                status_code=401, content={"message": "You must provide a token."}
            )
    except Exception as e:
        traceback.print_exc()
        return fastapi.responses.JSONResponse(
            status_code=500, content={"message": f"An error occurred: {e}"}
        )


@api.post(
    "/read/{endpoint}",
    description="Mark the 'meta' as read on the platform(s). "
                "[Note: Currently only used in the astroid Revolt-bot.]",
    responses={
        200: {"description": "Success"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal Server Error"},
    },
)
def mark_read(
        endpoint: int,
        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
        read_discord: bool = None,
        read_guilded: bool = None,
        read_revolt: bool = None,
):
    if token == data_token or token == Bot.config.MASTER_TOKEN:
        file = open(
            f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "r+"
        )
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
        return fastapi.responses.JSONResponse(
            status_code=401, content={"message": "The provided token is invalid."}
        )


@api.post(
    "/create",
    description="Create an endpoint.",
    response_description="Endpoints data.",
    responses={
        200: {"description": "Success", "content": {"application/json": {}}},
        401: {"description": "Unauthorized", "content": {"application/json": {}}},
        500: {
            "description": "Internal Server Error",
            "content": {"application/json": {}},
        },
    },
)
def create_endpoint(endpoint: int):
    try:
        file = open(
            f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json", "x"
        )
        data = {
            "config": {
                "self-user": False,
                "webhooks": {"discord": [], "guilded": [], "revolt": []},
                "channels": {"discord": [], "guilded": [], "revolt": []},
                "logs": {"discord": None, "guilded": None, "revolt": None},
                "blacklist": [],
                "allowed-ids": [],
                "isbeta": False,
            },
            "meta": {
                "sender-channel": None,
                "trigger": False,
                "sender": None,
                "read": {"discord": False, "guilded": False, "revolt": False},
                "message": {
                    "author": {"name": None, "avatar": None, "id": None},
                    "content": None,
                    "attachments": [],
                },
            },
        }
        json.dump(data, file)
        return fastapi.responses.JSONResponse(
            status_code=201, content={"message": "Created."}
        )
    except FileExistsError:
        return fastapi.responses.JSONResponse(
            status_code=403, content={"message": "This endpoint exists already."}
        )


@api.delete(
    "/delete/{endpoint}",
    description="Delete an endpoint.",
    responses={
        200: {"description": "Success"},
        401: {"description": "Unauthorized", "content": {"application/json": {}}},
        404: {"description": "Not Found", "content": {"application/json": {}}},
    },
)
def delete_endpoint(
        endpoint: int,
        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
):
    try:
        data_token = json.load(
            open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r")
        )[f"{endpoint}"]
        if token is not None:
            if token == data_token or token == Bot.config.MASTER_TOKEN:
                try:
                    os.remove(
                        f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json"
                    )
                except FileNotFoundError:
                    return fastapi.responses.JSONResponse(
                        status_code=404,
                        content={"message": "This endpoint does not exist."},
                    )
            else:
                return fastapi.responses.JSONResponse(
                    status_code=401,
                    content={"message": "The provided token is invalid."},
                )
        else:
            return fastapi.responses.JSONResponse(
                status_code=401, content={"message": "You must provide a token."}
            )
    except KeyError:
        return fastapi.responses.JSONResponse(
            status_code=404, content={"message": "This endpoint does not exist."}
        )


@api.delete(
    "/delete/data/{endpiont}",
    description="Edit or delete specific data of endpoint",
    responses={
        200: {"description": "Success"},
        401: {"description": "Unauthorized", "content": {"application/json": {}}},
        404: {"description": "Not Found", "content": {"application/json": {}}},
    },
)
def delete_enpoint_data(
        endpoint: int,
        webhook_discord: Annotated[
            str, fastapi.Query(max_length=350, min_length=50)
        ] = None,
        webhook_guilded: Annotated[
            str, fastapi.Query(max_length=350, min_length=50)
        ] = None,
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
        message_author_name: Annotated[
            str, fastapi.Query(max_length=50, min_length=1)
        ] = None,
        message_author_avatar: Annotated[
            str, fastapi.Query(max_length=250, min_length=50)
        ] = None,
        allowed_ids: Annotated[str, fastapi.Query(max_length=50, min_length=5)] = None,
        message_author_id: Annotated[
            str, fastapi.Query(max_length=50, min_length=5)
        ] = None,
        message_content: Annotated[str, fastapi.Query(max_length=1500)] = None,
        message_attachments: Annotated[
            str, fastapi.Query(max_length=1550, min_length=20)
        ] = None,
        token: Annotated[str, fastapi.Query(max_length=85, min_length=71)] = None,
):
    data_token = json.load(
        open(f"{pathlib.Path(__file__).parent.resolve()}/tokens.json", "r")
    )[f"{endpoint}"]
    if token is not None:
        if token == data_token or token == Bot.config.MASTER_TOKEN:
            try:
                json_file = open(
                    f"{pathlib.Path(__file__).parent.resolve()}/endpoints/{endpoint}.json",
                    "r+",
                )
                json_data = json.load(json_file)
                if webhook_discord:
                    print(
                        json_data["config"]["webhooks"]["discord"].index(
                            webhook_discord
                        )
                    )
                    json_data["config"]["webhooks"]["discord"][
                        json_data["config"]["webhooks"]["discord"].index(
                            webhook_discord
                        )
                    ] = None
                if webhook_guilded:
                    json_data["config"]["webhooks"]["guilded"][
                        json_data["config"]["webhooks"]["guilded"].index(
                            webhook_guilded
                        )
                    ] = None
                if webhook_revolt:
                    json_data["config"]["webhooks"]["revolt"][
                        json_data["config"]["webhooks"]["revolt"].index(webhook_revolt)
                    ] = None
                if log_discord:
                    json_data["config"]["logs"]["discord"][
                        json_data["config"]["logs"]["discord"].index(log_discord)
                    ] = None
                if log_guilded:
                    json_data["config"]["logs"]["guilded"][
                        json_data["config"]["logs"]["guilded"].index(log_guilded)
                    ] = None
                if log_revolt:
                    json_data["config"]["logs"]["revolt"][
                        json_data["config"]["logs"]["revolt"].index(log_revolt)
                    ] = None

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
                    json_data["config"]["channels"]["discord"][
                        json_data["config"]["config"]["discord"].index(channel_discord)
                    ] = None
                if channel_guilded:
                    json_data["config"]["channels"]["guilded"][
                        json_data["config"]["config"]["guilded"].index(channel_guilded)
                    ] = None
                if channel_revolt:
                    json_data["config"]["channels"]["revolt"][
                        json_data["config"]["config"]["revolt"].index(channel_revolt)
                    ] = None

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
                return fastapi.responses.JSONResponse(
                    status_code=404,
                    content={"message": "This endpoint does not exist."},
                )
        else:
            return fastapi.responses.JSONResponse(
                status_code=401, content={"message": "The provided token is invalid."}
            )
    else:
        return fastapi.responses.JSONResponse(
            status_code=401, content={"message": "You must provide a token."}
        )


uvicorn.run(api, host="localhost", port=9921)
