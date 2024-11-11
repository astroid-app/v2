import astroidapi.surrealdb_handler as surrealdb_handler
import asyncio
import astroidapi.errors as errors
import json


writes = {
    "config": {
        "self-user": "config.`self-user`",
        "type_webhooks": "config.webhooks",
        "webhooks": {
            "discord": "config.webhooks.discord",
            "guilded": "config.webhooks.guilded",
            "revolt": "config.webhooks.revolt",
            "nerimity": "config.webhooks.nerimity"
        },
        "type_channels": "config.channels",
        "channels": {
            "discord": "config.channels.discord",
            "guilded": "config.channels.guilded",
            "revolt": "config.channels.revolt",
            "nerimity": "config.channels.nerimity"
        },
        "type_logs": "config.logs",
        "logs": {
            "discord": "config.logs.discord",
            "guilded": "config.logs.guilded",
            "revolt": "config.logs.revolt",
            "nerimity": "config.logs.nerimity"
        },
        "blacklist": "config.blacklist",
        "allowed-ids": "config.`allowed-ids`",
        "isbeta": "config.isbeta"
    },
    "meta": {
        "_message_cache": "meta.`_message_cache`",
        "sender-channel": "meta.`sender-channel`",
        "trigger": "meta.trigger",
        "sender": "meta.sender",
        "type_read": "meta.read",
        "read": {
            "discord": "meta.read.discord",
            "guilded": "meta.read.guilded",
            "revolt": "meta.read.revolt",
            "nerimity": "meta.read.nerimity"
        },
        "type_message": "meta.message",
        "message": {
            "type_reply": "meta.message.reply",
            "isReply": "meta.message.isReply",
            "reply": {
            "message": "meta.message.reply.message",
            "author": "meta.message.reply.author"
        },
            "type_author": "meta.message.author",
            "author": {
                "name": "meta.message.author.name",
                "avatar": "meta.message.author.avatar",
                "id": "meta.message.author.id"
            },
            "content": "meta.message.content",
            "attachments": "meta.message.attachments"
        }
    }
}



class HealthCheck:

    @staticmethod
    def convert_keys_to_dotted(json_data, parent_key=""):
        dotted_dict = {}
        for key, value in json_data.items():
            if isinstance(value, dict):
                dotted_dict.update(HealthCheck.convert_keys_to_dotted(value, f"{parent_key}`{key}`."))
            else:
                dotted_dict[f"{parent_key}`{key}`"] = value
        return dotted_dict


    class EndpointCheck:
        @classmethod
        async def check(cls, endpoint):
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
                    "_message_cache": None,
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
                        "isReply": False,
                        "reply": {
                            "message": None,
                            "author": None
                        },
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
            try:
                endpoint_data = await surrealdb_handler.get_endpoint(endpoint, __file__)
                for key in healthy_endpoint_data["config"].keys():
                    if key not in endpoint_data["config"]:
                        raise errors.HealtCheckError.EndpointCheckError.EndpointConfigError(f"'{key}' not found in endpoint config '{endpoint}'")
                for key in healthy_endpoint_data["meta"].keys():
                    if key not in endpoint_data["meta"]:
                        raise errors.HealtCheckError.EndpointCheckError.EndpointMetaDataError(f"'{key}' not found in endpoint meta data '{endpoint}'")
                print("Endpoint is healthy")
                return True
            except IndexError as e:
                raise errors.HealtCheckError.EndpointCheckError(e)
    
        @classmethod
        async def repair_structure(cls, endpoint):
            healthy_endpoint_data = {
                "config": {
                    "self-user": False,
                    "type_webhooks": {},
                    "webhooks": {
                        "discord": [],
                        "guilded": [],
                        "revolt": [],
                        "nerimity": []
                    },
                    "type_channels": {},
                    "channels": {
                        "discord": [],
                        "guilded": [],
                        "revolt": [],
                        "nerimity": []
                    },
                    "type_logs": {},
                    "logs": {
                        "discord": "NULL",
                        "guilded": "NULL",
                        "revolt": "NULL",
                        "nerimity": "NULL"
                    },
                    "blacklist": [],
                    "allowed-ids": [],
                    "isbeta": False
                },
                "meta": {
                    "_message_cache": [],
                    "sender-channel": "NULL",
                    "trigger": False,
                    "sender": "NULL",
                    "type_read": {},
                    "read": {
                        "discord": False,
                        "guilded": False,
                        "revolt": False,
                        "nerimity": False
                    },
                    "type_message": {},
                    "message": {
                        "isReply": False,
                        "type_reply": {},
                        "reply": {
                            "message": "NULL",
                            "author": "NULL"
                        },
                        "type_author": {},
                        "author": {
                            "name": "NULL",
                            "avatar": "NULL",
                            "id": "NULL"
                        },
                        "content": "NULL",
                        "attachments": []
                    }
                }
            }
            try:
                endpoint_data = await surrealdb_handler.get_endpoint(endpoint, __file__)
                summary = []
                try:
                    self_user = endpoint_data["config"]["self-user"]
                    summary.append("✔ Self user found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["self-user"], healthy_endpoint_data["config"]["self-user"])
                    summary.append("✘ Self user not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    webhooks = endpoint_data["config"]["webhooks"]
                    summary.append("✔ Webhooks found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["type_webhooks"], healthy_endpoint_data["config"]["type_webhooks"])
                    summary.append("✘ Webhooks not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    webhooks_discord = endpoint_data["config"]["webhooks"]["discord"]
                    summary.append("✔ Webhooks - Discord found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["webhooks"]["discord"], healthy_endpoint_data["config"]["webhooks"]["discord"])
                    summary.append("✘ Webhooks - Discord not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    webhooks_guilded = endpoint_data["config"]["webhooks"]["guilded"]
                    summary.append("✔ Webhooks - Guilded found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["webhooks"]["guilded"], healthy_endpoint_data["config"]["webhooks"]["guilded"])
                    summary.append("✘ Webhooks - Guilded not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    webhooks_revolt = endpoint_data["config"]["webhooks"]["revolt"]
                    summary.append("✔ Webhooks - Revolt found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["webhooks"]["revolt"], healthy_endpoint_data["config"]["webhooks"]["revolt"])
                    summary.append("✘ Webhooks - Revolt not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    webhooks_nerimity = endpoint_data["config"]["webhooks"]["nerimity"]
                    summary.append("✔ Webhooks - Nerimity found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["webhooks"]["nerimity"], healthy_endpoint_data["config"]["webhooks"]["nerimity"])
                    summary.append("✘ Webhooks - Nerimity not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    channels = endpoint_data["config"]["channels"]
                    summary.append("✔ Channels found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["type_channels"], healthy_endpoint_data["config"]["type_channels"])
                    summary.append("✘ Channels not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    channels_discord = endpoint_data["config"]["channels"]["discord"]
                    summary.append("✔ Channels - Discord found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["channels"]["discord"], healthy_endpoint_data["config"]["channels"]["discord"])
                    summary.append("✘ Channels - Discord not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    channels_guilded = endpoint_data["config"]["channels"]["guilded"]
                    summary.append("✔ Channels - Guilded found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["channels"]["guilded"], healthy_endpoint_data["config"]["channels"]["guilded"])
                    summary.append("✘ Channels - Guilded not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    channels_revolt = endpoint_data["config"]["channels"]["revolt"]
                    summary.append("✔ Channels - Revolt found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["channels"]["revolt"], healthy_endpoint_data["config"]["channels"]["revolt"])
                    summary.append("✘ Channels - Revolt not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    channels_nerimity = endpoint_data["config"]["channels"]["nerimity"]
                    summary.append("✔ Channels - Nerimity found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["channels"]["nerimity"], healthy_endpoint_data["config"]["channels"]["nerimity"])
                    summary.append("✘ Channels - Nerimity not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    logs = endpoint_data["config"]["logs"]
                    summary.append("✔ Logs found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["type_logs"], healthy_endpoint_data["config"]["type_logs"])
                    summary.append("✘ Logs not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    logs_discord = endpoint_data["config"]["logs"]["discord"]
                    summary.append("✔ Logs - Discord found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["logs"]["discord"], healthy_endpoint_data["config"]["logs"]["discord"])
                    summary.append("✘ Logs - Discord not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    logs_guilded = endpoint_data["config"]["logs"]["guilded"]
                    summary.append("✔ Logs - Guilded found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["logs"]["guilded"], healthy_endpoint_data["config"]["logs"]["guilded"])
                    summary.append("✘ Logs - Guilded not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    logs_revolt = endpoint_data["config"]["logs"]["revolt"]
                    summary.append("✔ Logs - Revolt found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["logs"]["revolt"], healthy_endpoint_data["config"]["logs"]["revolt"])
                    summary.append("✘ Logs - Revolt not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    logs_nerimity = endpoint_data["config"]["logs"]["nerimity"]
                    summary.append("✔ Logs - Nerimity found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["logs"]["nerimity"], healthy_endpoint_data["config"]["logs"]["nerimity"])
                    summary.append("✘ Logs - Nerimity not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    blacklist = endpoint_data["config"]["blacklist"]
                    summary.append("✔ Blacklist found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["blacklist"], healthy_endpoint_data["config"]["blacklist"])
                    summary.append("✘ Blacklist not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    allowed_ids = endpoint_data["config"]["allowed-ids"]
                    summary.append("✔ Allowed IDs found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["allowed-ids"], healthy_endpoint_data["config"]["allowed-ids"])
                    summary.append("✘ Allowed IDs not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    isbeta = endpoint_data["config"]["isbeta"]
                    summary.append("✔ IsBeta found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["config"]["isbeta"], healthy_endpoint_data["config"]["isbeta"])
                    summary.append("✘ IsBeta not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    message_cache = endpoint_data["meta"]["_message_cache"]
                    summary.append("✔ Message Cache found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["_message_cache"], healthy_endpoint_data["meta"]["_message_cache"])
                    summary.append("✘ Message Cache not found. Adding...")
                try:
                    sender_channel = endpoint_data["meta"]["sender-channel"]
                    summary.append("✔ Meta - Sender Channel found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["sender-channel"], healthy_endpoint_data["meta"]["sender-channel"])
                    summary.append("✘ Meta - Sender Channel not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    trigger = endpoint_data["meta"]["trigger"]
                    summary.append("✔ Meta - Trigger found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["trigger"], healthy_endpoint_data["meta"]["trigger"])
                    summary.append("✘ Meta - Trigger not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    sender = endpoint_data["meta"]["sender"]
                    summary.append("✔ Meta - Sender found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["sender"], healthy_endpoint_data["meta"]["sender"])
                    summary.append("✘ Meta - Sender not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    read = endpoint_data["meta"]["read"]
                    summary.append("✔ Meta - Read found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["type_read"], healthy_endpoint_data["meta"]["type_read"])
                    summary.append("✘ Meta - Read not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    read_discord = endpoint_data["meta"]["read"]["discord"]
                    summary.append("✔ Meta - Read - Discord found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["read"]["discord"], healthy_endpoint_data["meta"]["read"]["discord"])
                    summary.append("✘ Meta - Read - Discord not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    read_guilded = endpoint_data["meta"]["read"]["guilded"]
                    summary.append("✔ Meta - Read - Guilded found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["read"]["guilded"], healthy_endpoint_data["meta"]["read"]["guilded"])
                    summary.append("✘ Meta - Read - Guilded not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    read_revolt = endpoint_data["meta"]["read"]["revolt"]
                    summary.append("✔ Meta - Read - Revolt found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["read"]["revolt"], healthy_endpoint_data["meta"]["read"]["revolt"])
                    summary.append("✘ Meta - Read - Revolt not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    read_nerimity = endpoint_data["meta"]["read"]["nerimity"]
                    summary.append("✔ Meta - Read - Nerimity found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["read"]["nerimity"], healthy_endpoint_data["meta"]["read"]["nerimity"])
                    summary.append("✘ Meta - Read - Nerimity not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    message = endpoint_data["meta"]["message"]
                    summary.append("✔ Meta - Message found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["type_message"], healthy_endpoint_data["meta"]["type_message"])
                    summary.append("✘ Meta - Message not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    is_reply = endpoint_data["meta"]["message"]["isReply"]
                    summary.append("✔ Meta - Message - IsReply found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["isReply"], healthy_endpoint_data["meta"]["message"]["isReply"])
                    summary.append("✘ Meta - Message - IsReply not found. Adding...")
                await asyncio.sleep(0.1)
                try:    
                    reply = endpoint_data["meta"]["message"]["reply"]
                    summary.append("✔ Meta - Message - Reply found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["type_reply"], healthy_endpoint_data["meta"]["message"]["type_reply"])
                    summary.append("✘ Meta - Message - Reply not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    reply_message = endpoint_data["meta"]["message"]["reply"]["message"]
                    summary.append("✔ Meta - Message - Reply - Message found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["reply"]["message"], healthy_endpoint_data["meta"]["message"]["reply"]["message"])
                    summary.append("✘ Meta - Message - Reply - Message not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    reply_author = endpoint_data["meta"]["message"]["reply"]["author"]
                    summary.append("✔ Meta - Message - Reply - Author found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["reply"]["author"], healthy_endpoint_data["meta"]["message"]["reply"]["author"])
                    summary.append("✘ Meta - Message - Reply - Author not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    message_author = endpoint_data["meta"]["message"]["author"]
                    summary.append("✔ Meta - Message - Author found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["type_author"], healthy_endpoint_data["meta"]["message"]["type_author"])
                    summary.append("✘ Meta - Message - Author not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    message_author_name = endpoint_data["meta"]["message"]["author"]["name"]
                    summary.append("✔ Meta - Message - Author - Name found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["author"]["name"], healthy_endpoint_data["meta"]["message"]["author"]["name"])
                    summary.append("✘ Meta - Message - Author - Name not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    message_author_avatar = endpoint_data["meta"]["message"]["author"]["avatar"]
                    summary.append("✔ Meta - Message - Author - Avatar found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["author"]["avatar"], healthy_endpoint_data["meta"]["message"]["author"]["avatar"])
                    summary.append("✘ Meta - Message - Author - Avatar not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    message_author_id = endpoint_data["meta"]["message"]["author"]["id"]
                    summary.append("✔ Meta - Message - Author - ID found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["author"]["id"], healthy_endpoint_data["meta"]["message"]["author"]["id"])
                    summary.append("✘ Meta - Message - Author - ID not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    message_content = endpoint_data["meta"]["message"]["content"]
                    summary.append("✔ Meta - Message - Content found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["content"], healthy_endpoint_data["meta"]["message"]["content"])
                    summary.append("✘ Meta - Message - Content not found. Adding...")
                await asyncio.sleep(0.1)
                try:
                    message_attachments = endpoint_data["meta"]["message"]["attachments"]
                    summary.append("✔ Meta - Message - Attachments found")
                except KeyError:
                    await surrealdb_handler.write_to_structure(endpoint, writes["meta"]["message"]["attachments"], healthy_endpoint_data["meta"]["message"]["attachments"])
                print("Endpoint structure repaired")
                print(summary)
                return summary
            except IndexError as e:
                raise errors.HealtCheckError.EndpointCheckError(e)
        
        @classmethod
        async def daily_check(cls):
            endpoints = await surrealdb_handler.get_all_endpoints()
            summary = []
            total_endpoints = len(endpoints)
            for endpoint in endpoints:
                print(f"[API - Healthcheck - Daily Endpoint Check] Checking {endpoint} | {endpoints.index(endpoint) + 1}/{total_endpoints}")
                try:
                    ishealthy = await cls.check(endpoint)
                    if ishealthy:
                        summary.append(f"{endpoint} | Healthy")
                except:
                    summary_line = ""
                    endpoint_summary = await cls.repair_structure(endpoint)
                    for line in endpoint_summary:
                        summary_line += f"{line} | "
                    summary.append(f"{endpoint} | {summary_line}")
                await asyncio.sleep(0.4)
            return summary

# asyncio.run(HealthCheck.EndpointCheck.repair_structure(1))