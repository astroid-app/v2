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
import asyncio

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

client = commands.Bot(command_prefix="a!")


client.help_command = None



async def send_iamup():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://status.astroid.cc/monitor/iamup/guilded") as r:
            if r.status == 200:
                print("Sent up status.")
            else:
                print("Could not send up status.")


async def iamup_loop():
    while True:
        asyncio.create_task(send_iamup())
        await asyncio.sleep(40)


async def fetch_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def post_json(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

@client.event
async def on_ready():
    print(f"Logged in as {client.user.name} - {client.user.id}")
    await client.loop.create_task(iamup_loop())


@client.event
async def on_message_delete(message: guilded.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.astroid.cc/getendpoint/guilded?id={message.server_id}&token={config.MASTER_TOKEN}") as response:
                data = await response.json()
                endpoint = data["discord"]
    except:
        traceback.print_exc()
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}") as response:
                data = await response.json()
                if data["config"]["isbeta"]:
                    return
    except IndexError:
        pass
    except KeyError:
        pass
    except:
        traceback.print_exc()

    channels_url = (
        f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}"
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
            f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}"
        )
        logs_data = await fetch_json(logs_url)

        channel = await client.fetch_channel(logs_data["config"]["logs"]["guilded"])
        await channel.send(embed=embed)


@client.event
async def on_message_edit(before: guilded.Message, after: guilded.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.astroid.cc/getendpoint/guilded?id={before.server_id}&token={config.MASTER_TOKEN}") as response:
                data = await response.json()
                endpoint = data["discord"]
    except:
        traceback.print_exc()
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}") as response:
                data = await response.json()
                if data["config"]["isbeta"]:
                    return
    except IndexError:
        pass
    except KeyError:
        pass
    except:
        traceback.print_exc()

    channels_url = (
        f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}"
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
            f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}"
        )
        logs_data = await fetch_json(logs_url)

        channel = await client.fetch_channel(logs_data["config"]["logs"]["guilded"])
        await channel.send(embed=embed)


@client.command()
async def register(ctx: commands.Context, endpoint):
    if endpoint == "":
        await ctx.send("Invalid Format: `a!register DISCORD_SERVER_ID`")
    else:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.astroid.cc/getendpoint/guilded?id={ctx.message.server_id}&token={config.MASTER_TOKEN}") as response:
                data = await response.json()
                try:
                    _endpoint = data["discord"]
                    if _endpoint == endpoint:
                        await ctx.send("Endpoint already registered.")
                        return
                    else:
                        await ctx.send("This server is registered with another endpoint. For further assistance, please contact the support server.")
                except KeyError:
                    async with aiohttp.ClientSession() as session: 
                        async with session.post(f"https://api.astroid.cc/createendpoint/guilded?endpoint={endpoint}&id={ctx.message.server_id}&token={config.MASTER_TOKEN}") as response:
                            if response.status == 200:
                                await ctx.send(f"Registered endpoint: https://api.astroid.cc/{endpoint}")
                            else:
                                await ctx.send(f"Oops, something went wrong: `{data['message']}`")
                except IndexError:
                    async with aiohttp.ClientSession() as session: 
                        async with session.post(f"https://api.astroid.cc/createendpoint/guilded?endpoint={endpoint}&id={ctx.message.server_id}&token={config.MASTER_TOKEN}") as response:
                            if response.status == 200:
                                await ctx.send(f"Registered endpoint: https://api.astroid.cc/{endpoint}")
                            else:
                                await ctx.send(f"Oops, something went wrong: `{data['message']}`")
                except TypeError:
                    async with aiohttp.ClientSession() as session: 
                        async with session.post(f"https://api.astroid.cc/createendpoint/guilded?endpoint={endpoint}&id={ctx.message.server_id}&token={config.MASTER_TOKEN}") as response:
                            if response.status == 200:
                                await ctx.send(f"Registered endpoint: https://api.astroid.cc/{endpoint}")
                            else:
                                await ctx.send(f"Oops, something went wrong: `{data['message']}`")
                except Exception as e:
                    await ctx.send(f"An error occurred while trying to register the endpoint. Please report this in the [Support Server](https://guilded.gg/astroid). \n\n`{e}`")

    try:
        channel_id = ctx.channel.id
        channel_webhook = await ctx.channel.create_webhook(name="astroid")
        channel_webhook_url = channel_webhook.url
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://api.astroid.cc/update/{endpoint}?channel_guilded={channel_id}&webhook_guilded={channel_webhook_url}&token={config.MASTER_TOKEN}") as response:
                data = await response.json()
                if response.ok:
                    await ctx.send(f"Updated endpoint: https://api.astroid.cc/{endpoint}")
                else:
                    await ctx.send(f"Oops, something went wrong: `{data['message']}`")
    except Exception as e:
        await ctx.send(f"An error occurred while trying to update the endpoint. Please report this in the [Support Server](https://guilded.gg/astroid). \n\n`{e}`")

@client.command()
async def help(ctx):
    embed = guilded.Embed(
        title="astroid", description="API Docs: https://api.astroid.cc/docs"
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
            "Invalid Format: `a!set-log DISCORD_SERVER_ID GUILDED_CHANNEL_ID`"
        )
    else:
        r = await post_json(
            f"https://api.astroid.cc/update/{endpoint}?channel_guilded={ctx.channel.id}&log_guilded={channelid}&token={config.MASTER_TOKEN}",
            {},
        )
        if r.ok:
            await ctx.send(
                f"Updated endpoint: https://api.astroid.cc/{endpoint}"
            )
        else:
            await ctx.send(f"{r['message']}")


@client.command()
async def allow(ctx, endpoint, allowid):
    if endpoint == "" or allowid == "":
        await ctx.send("Invalid Format: `a!allow DISCORD_SERVER_ID GUILDED_USER_ID`")
    else:
        r = await post_json(
            f"https://api.astroid.cc/update/{endpoint}?allowed_ids={allowid}&token={config.MASTER_TOKEN}",
            {},
        )
        if r.ok:
            await ctx.send(
                f"Updated endpoint: https://api.astroid.cc/{endpoint}"
            )
        else:
            await ctx.send(f"{r['message']}")


@client.command(aliases=["add-bridge"])
async def add_bridge(ctx, endpoint):
    if endpoint == "":
        await ctx.send("Invalid Format: `a!add-bridge DISCORD_SERVER_ID`")
    else:
        webhook = await ctx.channel.create_webhook(name="astroid")
        r = await post_json(
            f"https://api.astroid.cc/update/{endpoint}?channel_guilded={ctx.channel.id}&webhook_guilded={webhook.url}&token={config.MASTER_TOKEN}",
            {},
        )
        if r.ok:
            await ctx.send(
                f"Updated endpoint: https://api.astroid.cc/{endpoint}"
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
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.astroid.cc/getendpoint/guilded?id={message.server_id}&token={config.MASTER_TOKEN}") as response:
                data = await response.json()
                endpoint = data["discord"]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}") as response:
                    data = await response.json()
                    if data["config"]["isbeta"]:
                        return
        except IndexError:
            pass
        except KeyError:
            pass
        except TypeError:
            pass
        except:
            traceback.print_exc()
        await client.process_commands(message)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}"
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
                            channel = await client.fetch_channel(str(data["config"]["logs"]["guilded"]))
                            await channel.send(embed=embed)
                            return
                    allowed_ids = data["config"]["allowed-ids"]
                    if not message.author.bot or message.author.id in allowed_ids:
                        if not message.attachments and not message.embeds:
                            async with session.post(
                                f"https://api.astroid.cc/update/{endpoint}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url if message.author.avatar.url else 'https://api.astroid.cc/assets/Astroid PFP not found.png'}&message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}"
                            ) as response:
                                pass
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
                                    f"https://api.astroid.cc/update/{endpoint}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url if message.author.avatar.url else 'https://api.astroid.cc/assets/Astroid PFP not found.png'}&message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_attachments={message.attachments[0].url.replace('![]', '').replace('(', '').replace(')', '')}"
                                ) as response:
                                    pass
                        else:
                            attachments = ""
                            for attachment in message.attachments:
                                attachments += (
                                    attachment.url.replace("![]", "")
                                    .replace("(", "")
                                    .replace(")", "")
                                )
                            async with session.post(
                                f"https://api.astroid.cc/update/{endpoint}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url if message.author.avatar.url else 'https://api.astroid.cc/assets/Astroid PFP not found.png'}&message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_attachments={attachments[:-1]}"
                            ) as response:
                                pass
    except FileNotFoundError:
        await client.process_commands(message)
        pass
    except KeyError:
        await client.process_commands(message)
        pass
    except:
        await client.process_commands(message)
        traceback.print_exc()


client.run(config.GUILDED_TOKEN)
