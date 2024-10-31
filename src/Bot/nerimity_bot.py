import nerimity
import config
import pathlib
import json
import aiohttp
import asyncio
import os
import traceback
import requests



client = nerimity.Client(
    token=config.NERIMITY_TOKEN,
    prefix='a!',
)

async def send_message(endpoint, params):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.astroid.cc/update/{endpoint}?{params}&token={config.MASTER_TOKEN}") as resp:
            return await resp.json()

async def send_iamup():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://status.astroid.cc/monitor/iamup/nerimity") as r:
            if r.status == 200:
                print("Sent up status.")
            else:
                print(f"Could not send up status. ({r.status})")


async def iamup_loop():
    while True:
        asyncio.create_task(send_iamup())
        await asyncio.sleep(40)


@client.listen("on_message_create")
async def on_message_created(_message):
    message = nerimity.Message.deserialize(_message["message"])
    if message.content.startswith("a!") or message.content.startswith("gc!"):
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.astroid.cc/getendpoint/nerimity?id={nerimity.Context(message).server.id}&token={config.MASTER_TOKEN}") as response:
            data = await response.json()
            try:
                endpoint = data["discord"]
                if not endpoint:
                    return
            except:
                return
    try:
        if message.author.id == client.account.id:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.astroid.cc/{endpoint}?token={config.MASTER_TOKEN}") as resp:
                data = await resp.json()
                is_beta = data["config"]["isbeta"]
                if not is_beta:
                    if message.attachments:
                        if len(message.attachments) == 1:
                            params = f"message_author_id={message.author.id}&message_author_name={message.author.username}&message_author_avatar=https://cdn.nerimity.com/{message.author.avatar}"\
                            f"&message_content={message.content}&sender=nerimity&sender_channel={message.channel_id}&trigger=true&message_attachments=https://cdn.nerimity.com/{message.attachments[0].path}"
                            await send_message(endpoint, params)
                        else:
                            attachments = ""
                            for attachment in message.attachments:
                                attachments += f"https://cdn.nerimity.com/{attachment.path},"
                            params = f"message_author_id={message.author.id}&message_author_name={message.author.username}&message_author_avatar=https://cdn.nerimity.com/{message.author.avatar}"\
                            f"&message_content={message.content}&sender=nerimity&sender_channel={message.channel_id}&trigger=true&message_attachments={attachments[:-1]}"
                    if not message.attachments:
                        params = f"message_author_id={message.author.id}&message_author_name={message.author.username}&message_author_avatar=https://cdn.nerimity.com/{message.author.avatar}"\
                        f"&message_content={message.content}&sender=nerimity&sender_channel={message.channel_id}&trigger=true"
                        await send_message(endpoint, params)
    except:
        traceback.print_exc()
        pass


@client.command()
async def register(ctx: nerimity.Context, params: str):
    print(params)
    try:
        int(params[0])
    except Exception as e:
        await ctx.respond(f"Invalid endpoint. Please provide a valid endpoint. (Detail: `{e}`)")
        return
    endpoint = int(params[0])
    if ctx.author.id == client.account.id:
        return
    if len(params) == 0:
        await ctx.respond("Missing parameter: `endpoint`.\n Usage: `a!register [endpoint]`")
        return
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.astroid.cc/getendpoint/nerimity?id={ctx.server.id}&token={config.MASTER_TOKEN}") as response:
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
                    async with session.post(f"https://api.astroid.cc/createendpoint/nerimity?endpoint={endpoint}&id={ctx.server.id}&token={config.MASTER_TOKEN}") as response:
                        if response.status == 200:
                            await ctx.send(f"Registered endpoint: https://api.astroid.cc/{endpoint}")
                        else:
                            await ctx.send(f"Oops, something went wrong: `{data['message']}`")
            except IndexError:
                async with aiohttp.ClientSession() as session: 
                    async with session.post(f"https://api.astroid.cc/createendpoint/nerimity?endpoint={endpoint}&id={ctx.server.id}&token={config.MASTER_TOKEN}") as response:
                        if response.status == 200:
                            await ctx.send(f"Registered endpoint: https://api.astroid.cc/{endpoint}")
                        else:
                            await ctx.send(f"Oops, something went wrong: `{data['message']}`")
            except TypeError:
                async with aiohttp.ClientSession() as session: 
                    async with session.post(f"https://api.astroid.cc/createendpoint/nerimity?endpoint={endpoint}&id={ctx.server.id}&token={config.MASTER_TOKEN}") as response:
                        if response.status == 200:
                            await ctx.send(f"Registered endpoint: https://api.astroid.cc/{endpoint}")
                        else:
                            await ctx.send(f"Oops, something went wrong: `{data['message']}`")
            except Exception as e:
                await ctx.send(f"An error occurred while trying to register the endpoint. Please report this in the [Support Server](https://nerimity.com/i/fgE6q). \n\n`{e}`")

    try:
        channel_id = ctx.channel.id
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://api.astroid.cc/update/{endpoint}?channel_nerimity={channel_id}&token={config.MASTER_TOKEN}") as response:
                data = await response.json()
                if response.ok:
                    await ctx.send(f"Updated endpoint: https://api.astroid.cc/{endpoint}")
                else:
                    await ctx.send(f"Oops, something went wrong: `{data['message']}`")
    except Exception as e:
        await ctx.send(f"An error occurred while trying to update the endpoint. Please report this in the [Support Server](https://nerimity.com/i/fgE6q). \n\n`{e}`")
    


@client.command(aliases=["add-bridge"])
async def add_bridge(ctx: nerimity.Context, _args):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.astroid.cc/getendpoint/nerimity?id={ctx.server.id}&token={config.MASTER_TOKEN}") as response:
            data = await response.json()
            try:
                endpoint = data["discord"]
                if not endpoint:
                    await ctx.respond(":x: - Your endpoint could not be found.")
                    return
            except:
                await ctx.respond(":x: - Your endpoint could not be found.")
                return
    if endpoint:
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"https://api.astroid.cc/update/{endpoint}?channel_nerimity={ctx.channel.id}&token={config.MASTER_TOKEN}")
        await ctx.respond(f"Updated endpoint: https://api.astroid.cc/{endpoint}")
    else:
        await ctx.respond(":x: - Your endpoint could not be found.")

@client.listen("on_ready")
async def on_ready(client_info: dict):
    print(f"Logged in as {client.account.username}#{client.account.tag}")
    asyncio.create_task(iamup_loop())

client.run()