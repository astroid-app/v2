import traceback

import revolt
from revolt.ext import commands
import config
import os
import requests
import pathlib
import json
import asyncio
import aiohttp
import sentry_sdk

sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
) 

prefix = "gc!"


def get_endpoint(server: revolt.Server):
    print(server.id)
    try:
        return json.load(open(f"{pathlib.Path(__file__).parent.parent.resolve()}/revolt_servers/{server.id}.json", "r"))[
            "discord"]
    except:
        return False

class Client(commands.CommandsClient):
    def get_prefix(self, message: revolt.Message):
        return "gc!"

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        while True:
            for server in os.listdir(f"{pathlib.Path(__file__).parent.parent.resolve()}/revolt_servers"):
                try:
                    endpoint = int(
                        json.load(open(f"{pathlib.Path(__file__).parent.parent.resolve()}/revolt_servers/{server}", "r"))[
                            "discord"])
                    endpoint_request = requests.get(
                        f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}")
                    endpoint_json = endpoint_request.json()
                    endpoint_request.close()
                    if endpoint_json["meta"]["trigger"] is True and not endpoint_json["meta"]["sender"] == "revolt":
                        content = endpoint_json["meta"]["message"]["content"]
                        author_name = endpoint_json["meta"]["message"]["author"]["name"]
                        author_avatar = endpoint_json["meta"]["message"]["author"]["avatar"]
                        channel_ids_discord = endpoint_json["config"]["channels"]["discord"]
                        channel_ids_guilded = endpoint_json["config"]["channels"]["guilded"]
                        message_attachments = endpoint_json["meta"]["message"]["attachments"]
                        sender_channel = endpoint_json["meta"]["sender-channel"]
                        global channel_id
                        if str(sender_channel) in channel_ids_guilded or channel_ids_guilded is []:
                            print(endpoint_json["config"]["channels"]["revolt"])
                            channel_id = endpoint_json["config"]["channels"]["revolt"][
                                channel_ids_guilded.index(str(sender_channel))]
                        elif str(sender_channel) in channel_ids_discord:
                            channel_id = endpoint_json["config"]["channels"]["revolt"][
                                channel_ids_discord.index(str(sender_channel))]
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
                        if message_attachments:
                            if not content is None:
                                await channel.send(content=content,
                                                   masquerade=revolt.Masquerade(name=author_name,
                                                                                        avatar=author_avatar,
                                                                                        colour=color))
                            for attachment in message_attachments:
                                await channel.send(content=attachment,
                                                   masquerade=revolt.Masquerade(name=author_name,
                                                                                        avatar=author_avatar,
                                                                                        colour=color))
                            post = requests.post(
                                f"https://astroid.deutscher775.de/read/{endpoint}?token={config.MASTER_TOKEN}&read_revolt=true")
                            post.close()
                        else:
                            await channel.send(content=content,
                                               masquerade=revolt.Masquerade(name=author_name, avatar=author_avatar,
                                                                                    colour=color))
                            post = requests.post(
                                f"https://astroid.deutscher775.de/read/{endpoint}?token={config.MASTER_TOKEN}&read_revolt=true")
                            post.close()
                        await asyncio.sleep(2)

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


    async def on_message(self, message: revolt.Message):
        if not message.author.bot:
            if not message.content.lower().startswith(f"{prefix}help"):
                await self.handle_commands(message)
            if message.content.lower() == f"{prefix}help":
                embed = revolt.SendableEmbed(title="astroid", description="API Docs: https://astroid.deutscher775.de/docs\n\n"
                                                                             "**register** [discord_server_id]\n"
                                                                             "Register you server.\nNote: First register your discord server, then the other platform.\n"
                                                                             "**There is currently no command way to register without discord server. "
                                                                             "If you want to register without discord server, [click here](https://rvlt.gg/KQ611eqF)**.\n\n"
                                                                             "**set-log** [revolt_channel_id]\n"
                                                                             "Setup you log channel.\n\n"
                                                                             "**allow** [revolt_user_id]\n"
                                                                             "Allow a bot or webhook to be forwarded.\n\n"
                                                                             "**add-bridge**\n"
                                                                             "Add another channel to bridge over.\n"
                                                                             "Note: Works like `register`")
                await message.reply(embed=embed)
        try:
            endpoint_file = open(f"{pathlib.Path(__file__).parent.parent.resolve()}/revolt_servers/{message.server.id}.json",
                                 "r")
            endpoint = json.load(endpoint_file)["discord"]
            if message.channel.id in requests.get(
                    f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}").json()[
                "config"]["channels"][
                "revolt"]:
                try:
                    blacklist_request = requests.get(
                        f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}")
                    blacklist = blacklist_request.json()["config"]["blacklist"]
                    for word in blacklist:
                        if word is not None:
                            if word.lower() in message.content.lower():
                                embed = revolt.SendableEmbed(title=f"{message.author.name} - Flagged",
                                                              description=message.content)
                                channel_request = requests.get(
                                    f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}")
                                channel_json = channel_request.json()["config"]["logs"]["revolt"]
                                channel = await self.fetch_channel((channel_json))
                                channel_request.close()
                                await channel.send(embed=embed)
                                return
                        else:
                            pass
                    else:
                        allowed_ids_request = requests.get(
                            f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}")
                        allowed_ids = allowed_ids_request.json()["config"]["allowed-ids"]
                        allowed_ids_request.close()
                        if not message.author.bot or message.author.id in allowed_ids:
                            if not message.attachments:
                                requests.post(
                                    f"https://astroid.deutscher775.de/update/{endpoint}?message_content={message.content}&"
                                    f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                    f"message_author_id={message.author.id}&trigger=true&sender=revolt&token={config.MASTER_TOKEN}&"
                                    f"sender_channel={message.channel.id}")
                            if message.attachments:
                                if len(message.attachments) == 1:
                                    requests.post(
                                        f"https://astroid.deutscher775.de/update/{endpoint}?message_content={message.content}&"
                                        f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                        f"message_author_id={message.author.id}&trigger=true&sender=revolt&token={config.MASTER_TOKEN}"
                                        f"&sender_channel={message.channel.id}&message_attachments={message.attachments[0].url}/{message.attachments[0].filename}")
                                else:
                                    attachments = ""
                                    for attachment in message.attachments:
                                        attachments += f"{attachment.url}/{attachment.filename},"
                                    requests.post(
                                        f"https://astroid.deutscher775.de/update/{endpoint}?message_content={message.content}&"
                                        f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                        f"message_author_id={message.author.id}&trigger=true&sender=revolt&token={config.MASTER_TOKEN}"
                                        f"&sender_channel={message.channel.id}&message_attachments={attachments[:-1]}")

                except:
                    traceback.print_exc()
                    print(2)
                    pass
        except FileNotFoundError:
            pass


    async def register(self, ctx, endpoint: int = None):
        if endpoint is None:
            await ctx.reply("Missing parameter: `endpoint`.\n Usage: `gc!register` `[endpoint]`")
            return
        for server in os.listdir(f"{pathlib.Path(__file__).parent.parent.resolve()}/revolt_servers"):
            if server.endswith(".json"):
                try:
                    discord_server = json.load(open(server, "r"))["discord"]
                    if discord_server == endpoint:
                        await ctx.reply(
                            f"Enpoint exists already: https://astroid.deutscher775.de/{endpoint}")
                        return
                except:
                    pass
            else:
                pass

        try:
            data = {"discord": endpoint}
            json.dump(data,
                      open(
                          f"{pathlib.Path(__file__).parent.parent.resolve()}/revolt_servers/{ctx.message.channel.server.id}.json",
                          "x"))
        except FileExistsError:
            await ctx.reply(f"Enpoint exists already: https://astroid.deutscher775.de/{endpoint}")
            return
        # webhook = await message.channel.create_webhook(name="astroid")
        requests.post(
            f"https://astroid.deutscher775.de/update/{endpoint}?channel_revolt={ctx.message.channel.id}&"
            f"&token={config.MASTER_TOKEN}")
        await ctx.reply(f"Updated enpoint: https://astroid.deutscher775.de/{endpoint}")



    async def allow(self, ctx, allowid: str = None):
        if allowid is None:
            await ctx.reply("Missing parameter: `allow_id`.\n Usage: `gc!allow` `[allow_id]`")
            return
        endpoint = get_endpoint(ctx.server)
        if endpoint:
            requests.post(
                f"https://astroid.deutscher775.de/update/{endpoint}?allowed_ids={allowid}&token={config.MASTER_TOKEN}")
            await ctx.reply(f"Updated enpoint: https://astroid.deutscher775.de/{endpoint}")
        else:
            await ctx.reply(":x: - Your endpoint could not be found.")


    async def set_logs(self, ctx, channel: str = None):
        if channel is None:
            await ctx.reply("Missing parameter: `channel_id`.\n Usage: `gc!set-logs` `[channel_id]`")
            return
        endpoint = get_endpoint(ctx.server)
        if endpoint:
            requests.post(
                f"https://astroid.deutscher775.de/update/{endpoint}?"
                f"log_revolt={channel}&token={config.MASTER_TOKEN}")
            await ctx.reply(f"Updated enpoint: https://astroid.deutscher775.de/{endpoint}")
        else:
            await ctx.reply(":x: - Your endpoint could not be found.")


    async def add_bridge(self, ctx):
        endpoint = get_endpoint(ctx.server)
        if endpoint:
            requests.post(
                f"https://astroid.deutscher775.de/update/{endpoint}?channel_revolt={ctx.channel.id}&token={config.MASTER_TOKEN}")
            await ctx.reply(f"Updated enpoint: https://astroid.deutscher775.de/{endpoint}")
        else:
            await ctx.reply(":x: - Your endpoint could not be found.")



async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session, config.REVOLT_TOKEN)
        await client.start()

asyncio.run(main())
