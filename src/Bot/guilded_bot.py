import json
import os
import guilded
from guilded.ext import commands
import config
import aiohttp
import pathlib
import datetime
import traceback
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

client = commands.Bot(command_prefix="gc!")


client.help_command = None


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def post_json(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()


@client.event
async def on_message_delete(message: guilded.Message):
    endpoint_file = open(
        f"{pathlib.Path(__file__).parent.parent.resolve()}/Bot/guilded_servers/{message.server.id}.json",
        "r",
    )
    endpoint = json.load(endpoint_file)["discord"]

    channels_url = (
        f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}"
    )
    channels_data = await fetch_json(channels_url)

    if message.channel.id in channels_data["config"]["channels"]["guilded"]:
        embed = guilded.Embed(
            title=f"{message.author.name} - Deleted",
            description=message.content,
            colour=0xF5C400,
        )
        embed.add_field(
            name="Created at",
            value=f'{datetime.datetime.strftime(message.created_at, "%Y-%m-%d %H:%M.%S")} UTC',
        )

        logs_url = (
            f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}"
        )
        logs_data = await fetch_json(logs_url)

        channel = await client.fetch_channel(logs_data["config"]["logs"]["guilded"])
        await channel.send(embed=embed)


@client.event
async def on_message_edit(before: guilded.Message, after: guilded.Message):
    endpoint_file = open(
        f"{pathlib.Path(__file__).parent.parent.resolve()}/Bot/guilded_servers/{before.server.id}.json",
        "r",
    )
    endpoint = json.load(endpoint_file)["discord"]

    channels_url = (
        f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}"
    )
    channels_data = await fetch_json(channels_url)

    if before.channel.id in channels_data["config"]["channels"]["guilded"]:
        embed = guilded.Embed(
            title=f"{before.author.name} - Edited",
            description=after.content,
            colour=0xF5C400,
        )
        embed.add_field(name="Jump", value=f"[Jump]({after.jump_url})")
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)

        logs_url = (
            f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}"
        )
        logs_data = await fetch_json(logs_url)

        channel = await client.fetch_channel(logs_data["config"]["logs"]["guilded"])
        await channel.send(embed=embed)


@client.command()
async def register(ctx, endpoint):
    if endpoint == "":
        await ctx.send("Invalid Format: `gc!register DISCORD_SERVER_ID`")
    else:
        for server in os.listdir(
            f"{pathlib.Path(__file__).parent.parent.resolve()}/Bot/guilded_servers"
        ):
            if server.endswith(".json"):
                try:
                    discord_server = json.load(open(server, "r"))["discord"]
                    if discord_server == endpoint:
                        await ctx.send(
                            f"Endpoint already exists: https://astroid.deutscher775.de/{endpoint}"
                        )
                        return
                except:
                    pass
            else:
                pass

        try:
            data = {"discord": endpoint}
            json.dump(
                data,
                open(
                    f"{pathlib.Path(__file__).parent.parent.resolve()}/Bot/guilded_servers/{ctx.guild.id}.json",
                    "x",
                ),
            )
        except FileExistsError:
            await ctx.send(
                f"Endpoint already exists: https://astroid.deutscher775.de/{endpoint}"
            )
            return
        webhook = await ctx.channel.create_webhook(name="astroid")
        r = await post_json(
            f"https://astroid.deutscher775.de/update/{endpoint}?channel_guilded={ctx.channel.id}&webhook_guilded={webhook.url}&token={config.MASTER_TOKEN}",
            {},
        )
        if r.ok:
            await ctx.send(
                f"Updated endpoint: https://astroid.deutscher775.de/{endpoint}"
            )
        else:
            await ctx.send(f"{r['message']}")


@client.command()
async def help(ctx):
    embed = guilded.Embed(
        title="astroid", description="API Docs: https://astroid.deutscher775.de/docs"
    )
    embed.add_field(
        name="register",
        value="Register your server.\nNote: First register your discord server, then guilded.",
        inline=False,
    )
    embed.add_field(
        name="set-log",
        value="Setup your log channel.\nUsage: DISCORD_SERVER_ID GUILDED_CHANNEL_ID",
        inline=False,
    )
    embed.add_field(
        name="allow",
        value="Allow a bot or webhook to be forwarded.\nUsage: DISCORD_SERVER_ID USER_ID",
        inline=False,
    )
    embed.add_field(
        name="add-bridge",
        value="Add another channel to bridge over.\nNote: Works like `register`",
        inline=False,
    )
    await ctx.send(embed=embed)


@client.command()
async def set_log(ctx, endpoint, channelid):
    if endpoint == "" or channelid == "":
        await ctx.send(
            "Invalid Format: `gc!set-log DISCORD_SERVER_ID GUILDED_CHANNEL_ID`"
        )
    else:
        r = await post_json(
            f"https://astroid.deutscher775.de/update/{endpoint}?channel_guilded={ctx.channel.id}&log_guilded={channelid}&token={config.MASTER_TOKEN}",
            {},
        )
        if r.ok:
            await ctx.send(
                f"Updated endpoint: https://astroid.deutscher775.de/{endpoint}"
            )
        else:
            await ctx.send(f"{r['message']}")


@client.command()
async def allow(ctx, endpoint, allowid):
    if endpoint == "" or allowid == "":
        await ctx.send("Invalid Format: `gc!allow DISCORD_SERVER_ID GUILDED_USER_ID`")
    else:
        r = await post_json(
            f"https://astroid.deutscher775.de/update/{endpoint}?allowed_ids={allowid}&token={config.MASTER_TOKEN}",
            {},
        )
        if r.ok:
            await ctx.send(
                f"Updated endpoint: https://astroid.deutscher775.de/{endpoint}"
            )
        else:
            await ctx.send(f"{r['message']}")


@client.command(aliases=["add-bridge"])
async def add_bridge(ctx, endpoint):
    if endpoint == "":
        await ctx.send("Invalid Format: `gc!add-bridge DISCORD_SERVER_ID`")
    else:
        webhook = await ctx.channel.create_webhook(name="astroid")
        r = await post_json(
            f"https://astroid.deutscher775.de/update/{endpoint}?channel_guilded={ctx.channel.id}&webhook_guilded={webhook.url}&token={config.MASTER_TOKEN}",
            {},
        )
        if r.ok:
            await ctx.send(
                f"Updated endpoint: https://astroid.deutscher775.de/{endpoint}"
            )
        else:
            await ctx.send(f"{r['message']}")


@client.command()
async def send_embed(ctx):
    embed = guilded.Embed(title="Test Title", description="Test Description")
    embed.add_field(name="Test Field", value="Test Field Value")
    embed.set_image(url="https://media1.tenor.com/m/YYPY5tPFIE8AAAAd/bad-teeth.gif")
    embed.set_thumbnail(
        url="https://media.pinatafarm.com/protected/B183D0EF-49B8-47BF-A523-E72FD0CFFAAC/Soyjak-Pointing.2.meme.webp"
    )
    await ctx.send("Test Message", embed=embed)


@client.event
async def on_message(message: guilded.Message):
    async with aiohttp.ClientSession() as session:
        endpoint = json.load(open(f"{pathlib.Path(__file__).parent.parent.resolve()}/Bot/guilded_servers/{message.guild.id}.json", "r"))["discord"]
        async with session.get(f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}") as isbeta:
            isbeta = await isbeta.json()
            if isbeta.get("config").get("isbeta"):
                return
    await client.process_commands(message)
    try:
        endpoint_file = open(
            f"{pathlib.Path(__file__).parent.parent.resolve()}/Bot/guilded_servers/{message.server.id}.json",
            "r",
        )
        endpoint = json.load(endpoint_file)["discord"]
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://astroid.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}"
            ) as response:
                data = await response.json()
                if message.channel.id in data["config"]["channels"]["guilded"]:
                    blacklist = data["config"]["blacklist"]
                    for word in blacklist:
                        if word is not None and word.lower() in message.content.lower():
                            embed = guilded.Embed(
                                title=f"{message.author.name} - Flagged",
                                description=message.content,
                                colour=0xF5C400,
                            )
                            await message.delete()
                            channel = await client.fetch_channel(
                                str(data["config"]["logs"]["guilded"])
                            ).close()
                            await channel.send(embed=embed)
                            return
                    allowed_ids = data["config"]["allowed-ids"]
                    if not message.author.bot or message.author.id in allowed_ids:
                        if not message.attachments and not message.embeds:
                            async with session.post(
                                f"https://astroid.deutscher775.de/update/{endpoint}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}"
                            ) as response:
                                print(response.status, response.text)
                        elif message.embeds:
                            for field in message.embeds[0].fields:
                                embed["fields"].append(
                                    {
                                        "name": field.name,
                                        "value": field.value,
                                        "inline": str(field.inline).lower(),
                                    }
                                )
                        elif message.attachments:
                            if len(message.attachments) == 1:
                                async with session.post(
                                    f"https://astroid.deutscher775.de/update/{endpoint}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_attachments={message.attachments[0].url.replace('![]', '').replace('(', '').replace(')', '')}"
                                ) as response:
                                    print(response.status, response.text)
                        else:
                            attachments = ""
                            for attachment in message.attachments:
                                attachments += (
                                    attachment.url.replace("![]", "")
                                    .replace("(", "")
                                    .replace(")", "")
                                )
                            async with session.post(
                                f"https://astroid.deutscher775.de/update/{endpoint}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_attachments={attachments[:-1]}"
                            ) as response:
                                pass
    except FileNotFoundError:
        pass
    except KeyError:
        pass
    except:
        traceback.print_exc()


client.run(config.GUILDED_TOKEN)
