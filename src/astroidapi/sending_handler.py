import aiohttp
import nextcord
import guilded
import asyncio
from Bot import config
import astroidapi.errors as errors
import astroidapi.surrealdb_handler as surrealdb_handler
import astroidapi.read_handler as read_handler
import astroidapi.formatter as formatter
import astroidapi.attachment_processor as attachment_processor
import os
import traceback


class SendingHandler():
    def __init__(self):
        pass

    @classmethod
    async def distribute(cls, endpoint, updated_json):
        try:
            sender = updated_json["meta"]["sender"]

            registered_platforms = [platform for platform in updated_json["config"]["channels"] if len(updated_json["config"]["channels"][platform]) > 0]

            is_eligible = await surrealdb_handler.AttachmentProcessor.check_eligibility(endpoint)

            print(f"Is eligible: {is_eligible}")
            if is_eligible is True:
                if len(updated_json["meta"]["message"]["attachments"]) > 0:
                    attachments = []
                    for attachment in updated_json["meta"]["message"]["attachments"]:
                        file = await attachment_processor.download_attachment(attachment, registered_platforms)
                        attachments.append(file)
                else:
                    attachments = None
            else:
                attachments = None

            if sender == "guilded":
                await cls.send_from_guilded(updated_json, endpoint, attachments)
            if sender == "discord":
                await cls.send_from_discord(updated_json, endpoint, attachments)
            if sender == "revolt":
                await cls.send_from_revolt(updated_json, endpoint, attachments)
            if sender == "nerimity":
                await cls.send_from_nerimity(updated_json, endpoint, attachments)
            await attachment_processor.clear_temporary_attachments()
            return True
        except Exception as e:
            traceback.print_exc()
            raise errors.SendingError.DistributionError(e)
        

    @classmethod
    async def send_from_discord(cls, updated_json, endpoint, attachments: list = None):
        try:
            asyncio.create_task(cls.send_to_revolt(updated_json, endpoint, attachments))
            asyncio.create_task(cls.send_to_guilded(updated_json, endpoint, attachments))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_nerimity(updated_json, endpoint, attachments))
        except Exception as e:
            raise errors.SendingError.SendFromDiscordError(e)


    @classmethod
    async def send_from_nerimity(cls, updated_json, endpoint, attachments: list = None):
        try:
            asyncio.create_task(cls.send_to_discord(updated_json, endpoint, attachments))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_guilded(updated_json, endpoint, attachments))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_revolt(updated_json, endpoint, attachments))
            return True
        except Exception as e:
            raise errors.SendingError.SendFromNerimiryError(e)

    @classmethod
    async def send_from_revolt(cls, updated_json, endpoint, attachments: list = None):
        try:
            asyncio.create_task(cls.send_to_discord(updated_json, endpoint, attachments))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_guilded(updated_json, endpoint, attachments))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_nerimity(updated_json, endpoint, attachments))
            return True
        except Exception as e:
            raise errors.SendingError.SendFromRevoltError(e)
    
    @classmethod
    async def send_from_guilded(cls, updated_json, endpoint, attachments: list = None):
        try:
            asyncio.create_task(cls.send_to_discord(updated_json, endpoint, attachments))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_nerimity(updated_json, endpoint, attachments))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_revolt(updated_json, endpoint, attachments))
            return True
        except Exception as e:
            raise errors.SendingError.SendFromGuildedError(e)

    @classmethod
    async def send_to_discord(cls, updated_json, endpoint, attachments: list = None):
        try:
            read_discord = await read_handler.ReadHandler.check_read(endpoint, "discord")
            if read_discord is False:
                if updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["guilded"]:
                    webhook = updated_json["config"]["webhooks"]["discord"][updated_json["config"]["channels"]["guilded"].index(updated_json["meta"]["sender-channel"])]
                elif updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["nerimity"]:
                    webhook = updated_json["config"]["webhooks"]["discord"][updated_json["config"]["channels"]["nerimity"].index(updated_json["meta"]["sender-channel"])]
                elif updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["revolt"]:
                    webhook = updated_json["config"]["webhooks"]["discord"][updated_json["config"]["channels"]["revolt"].index(updated_json["meta"]["sender-channel"])]
                else:
                    raise errors.SendingError.ChannelNotFound(f'The channel {updated_json["meta"]["sender-channel"]} ({updated_json["meta"]["sender"]}) does not seem to be a registered channel on other platforms.')
                nextcord_files = []
                if attachments is not None:
                    for attachment in attachments:
                        file = nextcord.File(attachment.name, filename=attachment.name.split("/")[-1])
                        nextcord_files.append(file)
                        await surrealdb_handler.AttachmentProcessor.update_attachment(attachment.name.split("/")[-1].split(".")[0], sentby="discord")
                async with aiohttp.ClientSession() as session:
                    webhook_obj = nextcord.Webhook.from_url(webhook, session=session)
                    message_content = updated_json["meta"]["message"]["content"]
                    if message_content is None or message_content == "" or message_content == " ":
                        message_content = "||attachment||"
                    await webhook_obj.send(content=message_content, avatar_url=updated_json["meta"]["message"]["author"]["avatar"], username=formatter.Format.format_username(updated_json["meta"]["message"]["author"]["name"]), files=nextcord_files)
                    await session.close()
                    for file in nextcord_files:
                        file.close()
                asyncio.create_task(read_handler.ReadHandler.mark_read(endpoint, "discord"))
                print("Sent to discord")
                return True
            else:
                return False
        except errors.ReadHandlerError.AlreadyReadError:
            pass
        except Exception as e:
            raise errors.SendingError.SentToDiscordError(e)


    @classmethod
    async def send_to_guilded(cls, updated_json, endpoint, attachments: list = None):
        try:
            read_guilded = await read_handler.ReadHandler.check_read(endpoint, "guilded")
            if read_guilded is False:
                if updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["discord"]:
                    webhook = updated_json["config"]["webhooks"]["guilded"][updated_json["config"]["channels"]["discord"].index(updated_json["meta"]["sender-channel"])]
                elif updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["nerimity"]:
                    webhook = updated_json["config"]["webhooks"]["guilded"][updated_json["config"]["channels"]["nerimity"].index(updated_json["meta"]["sender-channel"])]
                elif updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["revolt"]:
                    webhook = updated_json["config"]["webhooks"]["guilded"][updated_json["config"]["channels"]["revolt"].index(updated_json["meta"]["sender-channel"])]
                else:
                    raise errors.SendingError.ChannelNotFound(f'The channel {updated_json["meta"]["sender-channel"]} ({updated_json["meta"]["sender"]}) does not seem to be a registered channel on other platforms.')
                guilded_files = []
                if attachments is not None:
                    for attachment in attachments:
                        file = guilded.File(attachment.name, filename=attachment.name.split("/")[-1])
                        guilded_files.append(file)
                        await surrealdb_handler.AttachmentProcessor.update_attachment(attachment.name.split("/")[-1].split(".")[0], sentby="guilded")
                
                async with aiohttp.ClientSession() as session:
                    asyncio.create_task(read_handler.ReadHandler.mark_read(endpoint, "guilded"))
                    webhook_obj = guilded.Webhook.from_url(webhook, session=session)
                    try:
                        message_content = updated_json["meta"]["message"]["content"]
                        if message_content is None or message_content == "" or message_content == " ":
                            message_content = "||attachment||"
                        await webhook_obj.send(content=message_content, avatar_url=updated_json["meta"]["message"]["author"]["avatar"], username=formatter.Format.format_username(updated_json["meta"]["message"]["author"]["name"]), files=guilded_files)
                    except AttributeError:
                        pass
                    for file in guilded_files:
                        file.close()
                    await session.close()
                print("Sent to guilded")
                return True
            else:
                return False
        except errors.ReadHandlerError.AlreadyReadError:
            pass
        except Exception as e:
            raise errors.SendingError.SentToGuildedError(e)
        

    @classmethod
    async def send_to_nerimity(cls, updated_json, endpoint, attachments: list = None):
        try:
            read_nerimity = await read_handler.ReadHandler.check_read(endpoint, "nerimity")
            if read_nerimity is False and updated_json["config"]["isbeta"] is True:
                async with aiohttp.ClientSession() as session:
                    response_json = updated_json
                    sender_channel = response_json["meta"]["sender-channel"]
                    discord_channels = response_json["config"]["channels"]["discord"]
                    if sender_channel in discord_channels:
                        channel_id = response_json["config"]["channels"]["nerimity"][discord_channels.index(sender_channel)]
                    elif sender_channel in response_json["config"]["channels"]["guilded"]:
                        channel_id = response_json["config"]["channels"]["nerimity"][response_json["config"]["channels"]["guilded"].index(sender_channel)]
                    elif sender_channel in response_json["config"]["channels"]["revolt"]:
                        channel_id = response_json["config"]["channels"]["nerimity"][response_json["config"]["channels"]["revolt"].index(sender_channel)]
                    else:
                        raise errors.SendingError.ChannelNotFound(f'The channel {sender_channel} ({updated_json["meta"]["sender"]}) does not seem to be a registered channel on other platforms.')
                    message_author_name = response_json["meta"]["message"]["author"]["name"]
                    message_content = response_json["meta"]["message"]["content"]
                    headers = {
                        "Authorization": f"{config.NERIMITY_TOKEN}",
                    }
                    print(channel_id)
                    formdata = aiohttp.FormData()
                    formdata.add_field("content", f"**{message_author_name}**: {message_content}")
                    if attachments is not None:
                        formdata.add_field("attachment", open(os.path.abspath(attachments[0].name), "rb"), filename=attachments[0].name.split("/")[-1], content_type=f"image/{attachments[0].name.split('.')[-1]}")
                    r = await session.post(f"https://nerimity.com/api/channels/{int(channel_id)}/messages", headers=headers, data=formdata)
                    print(f"Sent to nerimity. Response: {r.status}, {r.reason} {await r.text()}")
                    await session.close()
                    if attachments is not None:
                        await surrealdb_handler.AttachmentProcessor.update_attachment(attachments[0].name.split("/")[-1].split(".")[0], sentby="nerimity")
                    asyncio.create_task(read_handler.ReadHandler.mark_read(endpoint, "nerimity"))
                    print("Sent to nerimity")
                    return True
            else:
                return False
        except Exception as e:
            raise errors.SendingError.SendFromNerimiryError(e)
        
    
    @classmethod
    async def send_to_revolt(cls, updated_json, endpoint, attachments: list = None):
        return True
        #if updated_json["meta"]["read"]["revolt"] is False:
        #    if updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["discord"]:
        #        channel_id = updated_json["config"]["channels"]["revolt"][updated_json["config"]["channels"]["discord"].index(updated_json["meta"]["sender-channel"])]
        #    elif updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["guilded"]:
        #        channel_id = updated_json["config"]["channels"]["revolt"][updated_json["config"]["channels"]["guilded"].index(updated_json["meta"]["sender-channel"])]
        #    elif updated_json["meta"]["sender-channel"] in updated_json["config"]["channels"]["nerimity"]:
        #        channel_id = updated_json["config"]["channels"]["revolt"][updated_json["config"]["channels"]["nerimity"].index(updated_json["meta"]["sender-channel"])]
        #    else:
        #        raise errors.SendingError.ChannelNotFound(f"The channel {updated_json["meta"]["sender-channel"]} ({updated_json["meta"]["sender"]}) does not seem to be a registered channel on other platforms.")
        #    
        #    headers = {
        #        "Authorization" : f"Bot {config.REVOLT_TOKEN}"
        #    }
        #    url = f"https://api.revolt.chat/channels/{channel_id}/messages"
        #    payload = {
        #        "attachments": [None],
        #        "masquerade": {
        #            "avatar": updated_json["meta"]["message"]["author"]["avatar"],
        #            "name": updated_json["meta"]["message"]["author"]["name"]
        #        
        #        },
        #        "replies": [
        #            {
        #                "id": "",
        #                "mention": True
        #            }
        #        ],
        #        "embeds": [{}]
        #    }
        #    async with aiohttp.ClientSession() as session:
        #        async with session.post(url, headers=headers, json=payload) as r:
        #            await session.post(f"https://astroid.deutscher775.de/read/{endpoint}?token={config.MASTER_TOKEN}&read_revolt=true")
        #            await session.close()
        #        return True
        #else:
        #    return False
            