import datetime
import json
import os
import asyncio
import traceback
import revolt.errors
import aiohttp
import revolt
from revolt.ext import commands
import config
import pathlib
import requests
import logging


logger = logging.getLogger('revolt')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='revolt.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class Client(revolt.Client):
    async def on_ready(self):
        await self.edit_status(text="gc!help | Watching your server")
        while True:
            for server in os.listdir(f"{pathlib.Path(__file__).parent.resolve()}/revolt_servers"):
                try:
                    endpoint = int(
                        json.load(open(f"{pathlib.Path(__file__).parent.resolve()}/revolt_servers/{server}", "r"))[
                            "discord"])
                    endpoint_request = requests.get(
                        f"https://guildcord-api.tk/{endpoint}?token={config.MASTER_TOKEN}")
                    endpoint_json = endpoint_request.json()
                    endpoint_request.close()
                    if endpoint_json["meta"]["trigger"] is True:
                        content = endpoint_json["meta"]["message"]["content"]
                        author_name = endpoint_json["meta"]["message"]["author"]["name"]
                        author_avatar = endpoint_json["meta"]["message"]["author"]["avatar"]
                        channel_ids_discord = endpoint_json["config"]["channels"]["discord"]
                        channel_ids_guilded = endpoint_json["config"]["channels"]["guilded"]
                        sender_channel = endpoint_json["meta"]["sender-channel"]
                        global channel_id
                        if str(sender_channel) in channel_ids_guilded:
                            channel_id = endpoint_json["config"]["channels"]["revolt"][
                                channel_ids_guilded.index(str(sender_channel))]
                        elif int(sender_channel) in channel_ids_discord:
                            channel_id = endpoint_json["config"]["channels"]["revolt"][channel_ids_discord.index(int(sender_channel))]
                        sender = endpoint_json["meta"]["sender"]
                        print(channel_id)
                        channel = await self.fetch_channel(channel_id)
                        print(channel.name)
                        global color
                        if sender == "discord":
                            color = "#0591fc"
                        elif sender == "guilded":
                            color = "#fcd705"
                        else:
                            color = "#fc0516"
                        await channel.send(content=content,
                                           masquerade=revolt.Masquerade(name=author_name, avatar=author_avatar,
                                                                        colour=color))
                        post = requests.post(
                            f"https://guildcord-api.tk/read/{endpoint}?token={config.MASTER_TOKEN}&read_revolt=true")
                        post.close()
                except FileNotFoundError:
                    print("No file found")
                    pass
                except KeyError:
                    print("Invalid json")
                    pass
                except revolt.errors.HTTPError:
                    traceback.print_exc()
                    print("Channel not found")
                    pass
                except json.decoder.JSONDecodeError:
                    pass
                except:
                    traceback.print_exc()
            await asyncio.sleep(2)

    async def on_message(self, message):
        if message.content.startswith("gc!"):
            global endpoint
            if message.content.startswith("gc!register"):
                try:
                    endpoint = int(message.content.replace("gc!register ", ""))
                except ValueError:
                    await message.channel.send("Invalid Format: `gc!register DISCORD_SERVER_ID`")
                    return
                print(endpoint)
                if endpoint == "":
                    await message.channel.send("Invalid Format: `gc!register DISCORD_SERVER_ID`")
                else:
                    for server in os.listdir(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers"):
                        if server.endswith(".json"):
                            try:
                                discord_server = json.load(open(server, "r"))["discord"]
                                if discord_server == endpoint:
                                    await message.channel.send(
                                        f"Enpoint exists already: https://guildcord-api.tk/{endpoint}")
                                    return
                            except:
                                pass
                        else:
                            pass

                    try:
                        data = {"discord": endpoint}
                        json.dump(data,
                                  open(
                                      f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{message.guild.id}.json",
                                      "x"))
                    except FileExistsError:
                        await message.channel.send(f"Enpoint exists already: https://guildcord-api.tk/{endpoint}")
                        return
                    webhook = await message.channel.create_webhook(name="Guildcord")
                    requests.post(
                        f"https://guildcord-api.tk/update/{endpoint}?channel_guilded={message.channel.id}&"
                        f"webhook_guilded={webhook.url}&token={config.MASTER_TOKEN}")
                    await message.channel.send(f"Updated enpoint: https://guildcord-api.tk/{endpoint}")
            if message.content.startswith("gc!help"):
                embed = revolt.SendableEmbed(title="Guildcord", description="API Docs: https://guildcord-api.tk/docs\n\n"
                                                                            "**register**\n"
                                                                            "Register you server.\nNote: First register your discord server, then the other platform.\n\n"
                                                                            "**set-log**\n"
                                                                            "Setup you log channel.\nUsage: DISCORD_SERVER_ID REVOLT_CHANNEL_ID\n\n"
                                                                            "**allow**\n"
                                                                            "Allow a bot or webhook to be forwarded.\nUsage: DISCORD_SERVER_ID USER_ID\n\n"
                                                                            "**add-bridge**\n"
                                                                            "Add another channel to bridge over.\n"
                                                                            "Note: Works like `register`")
                await message.channel.send(embed=embed)
            if message.content.startswith("gc!set-log"):
                try:
                    endpoint = int(message.content.replace("gc!set-log ", "").split(" ")[0])
                except ValueError:
                    await message.channel.send("Invalid Format: `gc!set-log DISCORD_SERVER_ID GUILDED_CHANNEL_ID`")
                    return
                channelid = message.content.replace("gc!set-log ", "").split(" ")[1]
                if endpoint == "" or channelid == "":
                    await message.channel.send("Invalid Format: `gc!set-log DISCORD_SERVER_ID GUILDED_CHANNEL_ID`")
                else:
                    requests.post(
                        f"https://guildcord-api.tk/update/{endpoint}?channel_guilded={message.channel.id}&"
                        f"log_guilded={channelid}&token={config.MASTER_TOKEN}")
                    await message.channel.send(f"Updated enpoint: https://guildcord-api.tk/{endpoint}")

            if message.content.startswith("gc!allow"):
                try:
                    endpoint = int(message.content.replace("gc!allow ", "").split(" ")[0])
                    print(endpoint)
                except ValueError:
                    print(1)
                    await message.channel.send("Invalid Format: `gc!allow DISCORD_SERVER_ID GUILDED_USER_ID`")
                    return
                allowid = message.content.replace("gc!allow ", "").split(" ")[1]
                print(allowid)
                if endpoint == "" or allowid == "":
                    await message.channel.send("Invalid Format: `gc!allow DISCORD_SERVER_ID GUILDED_USER_ID`")
                else:
                    requests.post(
                        f"https://guildcord-api.tk/update/{endpoint}?allowed_ids={allowid}&token={config.MASTER_TOKEN}")
                    await message.channel.send(f"Updated enpoint: https://guildcord-api.tk/{endpoint}")

            if message.content.startswith("gc!add-bridge"):
                try:
                    endpoint = int(message.content.replace("gc!add-bridge ", ""))
                except ValueError:
                    await message.channel.send("Invalid Format: `gc!add-bridge DISCORD_SERVER_ID`")
                    return
                print(endpoint)
                if endpoint == "":
                    await message.channel.send("Invalid Format: `gc!add-bridge DISCORD_SERVER_ID`")
                else:
                    requests.post(
                        f"https://guildcord-api.tk/update/{endpoint}?channel_revolt={message.channel.id}&token={config.MASTER_TOKEN}")
                    await message.channel.send(f"Updated enpoint: https://guildcord-api.tk/{endpoint}")
        else:
            try:
                endpoint_file = open(f"{pathlib.Path(__file__).parent.resolve()}/revolt_servers/{message.server.id}.json",
                                     "r")
                endpoint = json.load(endpoint_file)["discord"]
                if message.channel.id in requests.get(
                        f"https://guildcord-api.tk/{endpoint}?token={config.MASTER_TOKEN}").json()[
                    "config"]["channels"][
                    "revolt"]:
                    try:
                        blacklist_request = requests.get(
                            f"https://guildcord-api.tk/{endpoint}?token={config.MASTER_TOKEN}")
                        blacklist = blacklist_request.json()["config"]["blacklist"]
                        for word in blacklist:
                            if word is not None:
                                if word.lower() in message.content.lower():
                                    embed = revolt.Embed(title=f"{message.author.name} - Flagged",
                                                         description=message.content, colour=0xf5c400)
                                    channel_request = requests.get(
                                        f"https://guildcord-api.tk/{endpoint}?token={config.MASTER_TOKEN}")
                                    channel_json = channel_request.json()["config"]["logs"]["revolt"]
                                    channel = await self.fetch_channel(channel_json)
                                    channel_request.close()
                                    await channel.send(embed=embed)
                                    return
                            else:
                                pass
                        else:
                            allowed_ids_request = requests.get(
                                f"https://guildcord-api.tk/{endpoint}?token={config.MASTER_TOKEN}")
                            allowed_ids = allowed_ids_request.json()["config"]["allowed-ids"]
                            allowed_ids_request.close()
                            if not message.author.bot or message.author.id in allowed_ids:
                                if not message.attachments:
                                    post = requests.post(
                                        f"https://guildcord-api.tk/update/{endpoint}?message_content={message.content}&"
                                        f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                        f"message_author_id={message.author.id}&trigger=true&sender=revolt&token={config.MASTER_TOKEN}"
                                        f"&sender_channel={message.channel.id}")
                                    post.close()

                    except:
                        traceback.print_exc()
                        print(2)
                        pass
            except FileNotFoundError:
                pass


async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, config.REVOLT_TOKEN)
        await client.start()


asyncio.run(main())
