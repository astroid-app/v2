import aiohttp
import nextcord
import guilded
import asyncio
from Bot import config
import astroidapi.errors as errors
import astroidapi.surrealdb_handler as surrealdb_handler
import astroidapi.read_handler as read_handler


class SendingHandler():
    def __init__(self):
        pass

    @classmethod
    async def distribute(cls, endpoint, updated_json):
        try:
            sender = updated_json["meta"]["sender"]

            if sender == "guilded":
                await cls.send_from_guilded(updated_json, endpoint)
            if sender == "discord":
                await cls.send_from_discord(updated_json, endpoint)
            if sender == "revolt":
                await cls.send_from_revolt(updated_json, endpoint)
            if sender == "nerimity":
                await cls.send_from_nerimity(updated_json, endpoint)
            return True
        except Exception as e:
            raise errors.SendingError.DistributionError(e)
        


    @classmethod
    async def send_from_discord(cls, updated_json, endpoint):
        try:
            asyncio.create_task(cls.send_to_revolt(updated_json, endpoint))
            asyncio.create_task(cls.send_to_guilded(updated_json, endpoint))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_nerimity(updated_json, endpoint))
        except Exception as e:
            raise errors.SendingError.SendFromDiscordError(e)


    @classmethod
    async def send_from_nerimity(cls, updated_json, endpoint):
        try:
            asyncio.create_task(cls.send_to_discord(updated_json, endpoint))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_guilded(updated_json, endpoint))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_revolt(updated_json, endpoint))
            return True
        except Exception as e:
            raise errors.SendingError.SendFromNerimiryError(e)

    @classmethod
    async def send_from_revolt(cls, updated_json, endpoint):
        try:
            asyncio.create_task(cls.send_to_discord(updated_json, endpoint))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_guilded(updated_json, endpoint))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_nerimity(updated_json, endpoint))
            return True
        except Exception as e:
            raise errors.SendingError.SendFromRevoltError(e)
    
    @classmethod
    async def send_from_guilded(cls, updated_json, endpoint):
        try:
            asyncio.create_task(cls.send_to_discord(updated_json, endpoint))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_nerimity(updated_json, endpoint))
            if updated_json["config"]["isbeta"] is True:
                asyncio.create_task(cls.send_to_revolt(updated_json, endpoint))
            return True
        except Exception as e:
            raise errors.SendingError.SendFromGuildedError(e)

    @classmethod
    async def send_to_discord(cls, updated_json, endpoint):
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
                async with aiohttp.ClientSession() as session:
                    webhook_obj = nextcord.Webhook.from_url(webhook, session=session)
                    await webhook_obj.send(content=updated_json["meta"]["message"]["content"], avatar_url=updated_json["meta"]["message"]["author"]["avatar"], username=updated_json["meta"]["message"]["author"]["name"])
                    await session.close()
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
    async def send_to_guilded(cls, updated_json, endpoint):
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
                async with aiohttp.ClientSession() as session:
                    webhook_obj = guilded.Webhook.from_url(webhook, session=session)
                    await webhook_obj.send(content=updated_json["meta"]["message"]["content"], avatar_url=updated_json["meta"]["message"]["author"]["avatar"], username=updated_json["meta"]["message"]["author"]["name"])
                    await session.close()
                asyncio.create_task(read_handler.ReadHandler.mark_read(endpoint, "guilded"))
                print("Sent to guilded")
                return True
            else:
                return False
        except errors.ReadHandlerError.AlreadyReadError:
            pass
        except Exception as e:
            raise errors.SendingError.SentToGuildedError(e)
        

    @classmethod
    async def send_to_nerimity(cls, updated_json, endpoint):
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
                    body = {
                        "content": f"**{message_author_name}**: {message_content}"
                    }
                    await session.post(f"https://nerimity.com/api/channels/{int(channel_id)}/messages", headers=headers, data=body)
                    await session.close()
                    asyncio.create_task(read_handler.ReadHandler.mark_read(endpoint, "nerimity"))
                    print("Sent to nerimity")
                    return True
            else:
                return False
        except Exception as e:
            raise errors.SendingError.SendFromNerimiryError(e)
        
    
    @classmethod
    async def send_to_revolt(cls, updated_json, endpoint):
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
            