import datetime
import traceback
import logging
import nextcord
from nextcord.ext import commands
import config
import aiohttp
import requests

logger = logging.getLogger('nextcord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = commands.Bot(command_prefix="gc!", intents=nextcord.Intents.all())


@client.event
async def on_message_delete(message: nextcord.Message):
    session = aiohttp.ClientSession()
    async with session.get(
            f"https://guildcord-api.tk/{message.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
        channel_json = await channel_request.json()
        channel_request.close()
    if message.channel.id in channel_json["config"]["channels"]["discord"]:
        embed = nextcord.Embed(title=f"{message.author.name} - Deleted", description=message.content, colour=0xf5c400)
        embed.add_field(name="Created at",
                        value=f'{datetime.datetime.strftime(message.created_at, "%Y-%m-%d %H:%M:%S")} UTC')
        async with session.get(
                f"https://guildcord-api.tk/{message.guild.id}?token={config.MASTER_TOKEN}") as log_request:
            log_json = await log_request.json()
            await client.get_channel(log_json["config"]["logs"]["discord"]).send(embed=embed)
            await session.close()


@client.event
async def on_message_edit(before: nextcord.Message, after: nextcord.Message):
    session = aiohttp.ClientSession()
    async with session.get(
            f"https://guildcord-api.tk/{before.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
        channel_json = await channel_request.json()
        channel_request.close()
    if before.channel.id in channel_json["config"]["channels"]["discord"]:
        embed = nextcord.Embed(title=f"{before.author.name} - Edited", description=after.content, colour=0xf5c400)
        embed.add_field(name="Jump", value=after.jump_url)
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        async with session.get(
                f"https://guildcord-api.tk/{before.guild.id}?token={config.MASTER_TOKEN}") as log_request:
            log_json = await log_request.json()
            await client.get_channel(log_json["config"]["logs"]["discord"]).send(embed=embed)
            await session.close()


@client.event
async def on_message(message: nextcord.Message):
    session = aiohttp.ClientSession()
    try:
        async with session.get(
                f"https://guildcord-api.tk/{message.guild.id}?token={config.MASTER_TOKEN}") as discord_channel_request:
            discord_channel = await discord_channel_request.json()
            discord_channel_request.close()
        if message.channel.id in discord_channel["config"]["channels"]["discord"]:
            global blacklist
            async with session.get(
                    f"https://guildcord-api.tk/{message.guild.id}?token={config.MASTER_TOKEN}") as blacklist_reqeust:
                blacklist = await blacklist_reqeust.json()
                blacklist_reqeust.close()
            for word in blacklist["config"]["blacklist"]:
                if word is not None:
                    if word.lower() in message.content.lower():
                        embed = nextcord.Embed(title=f"{message.author.name} - Flagged", description=message.content,
                                               colour=0xf5c400)
                        await message.delete()
                        async with session.get(
                                f"https://guildcord-api.tk/{message.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
                            channel = await channel_request.json()
                            channel_request.close()
                        await client.get_channel(channel["config"]["logs"]["discord"]).send(embed=embed)
                        await session.close()
                        return
                    else:
                        pass

            else:
                global allowed_ids
                async with session.get(
                        f"https://guildcord-api.tk/{message.guild.id}?token={config.MASTER_TOKEN}") as allowed_ids_request:
                    allowed_ids = await allowed_ids_request.json()
                    allowed_ids_request.close()
                if not message.author.bot or message.author.id in allowed_ids["config"]["allowed-ids"]:
                    if not message.attachments:
                        await session.post(
                            f"https://guildcord-api.tk/update/{message.channel.guild.id}?message_content={message.content}&"
                            f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                            f"message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&"
                            f"sender_channel={message.channel.id}")
                        await session.close()
                        await session.connector.close()
                    if message.attachments:
                        if len(message.attachments) == 1:
                            await session.post(
                                f"https://guildcord-api.tk/update/{message.channel.guild.id}?message_content={message.content}&"
                                f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                f"message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}"
                                f"&sender_channel={message.channel.id}&message_attachments={message.attachments[0].url}")
                            await session.close()
                        else:
                            attachments = ""
                            for attachment in message.attachments:
                                attachments += attachment.url
                            await session.post(
                                f"https://guildcord-api.tk/update/{message.channel.guild.id}?message_content={message.content}&"
                                f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                f"message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}"
                                f"&sender_channel={message.channel.id}&message_attachments={attachments[:-1]}")
                            await session.close()

        else:
            await session.close()

    except:
        await session.close()
        traceback.print_exc()
        pass


@client.slash_command(name="register", default_member_permissions=8, description="Automatically register your server.")
async def register(interaction: nextcord.Interaction):
    session = aiohttp.ClientSession()
    await interaction.response.send_message("Starting registering process.. (This may take a while.)", ephemeral=True)
    try:
        webhook = await interaction.channel.create_webhook(name="Guildcord")
        async with session.post(f"https://guildcord-api.tk/create?endpoint={interaction.guild.id}") as create_request:
            create_request.close()
            pass
        await interaction.edit_original_message(content="Created endpoint. Updating values.. (This may take a while.)")
        async with session.post(
                f"https://guildcord-api.tk/update/{interaction.channel.guild.id}?channel_discord={interaction.channel.id}&"
                f"webhook_discord={webhook.url}&token={config.MASTER_TOKEN}") as update_request:
            update_request.close()
            pass
        await interaction.edit_original_message(content="Updated values. Requesting token.. (This may take a while.)")
        async with session.post(
                f"https://guildcord-api.tk/token/{interaction.guild.id}?master_token={config.MASTER_TOKEN}") as token_request:
            token_data = await token_request.json()
            token = token_data["token"]
            token_request.close()
        await interaction.edit_original_message(content="Done.")
        await interaction.edit_original_message(content=
            f"Created enpoint: https://guildcord-api.tk/{interaction.guild.id}\n"
            f"Your API Token is: `{token}`\n"
            f"Save this and **__do not__** share this!\n"
            f"Hop over to Guilded and run this command in the channel, you want do bridge over:"
            f"`gc!register {interaction.guild.id}`")

    except:
        traceback.print_exc()
    finally:
        await session.close()


@client.slash_command(name="add-bridge", description="Add another channel for bridging")
async def add_bridge(interaction: nextcord.Interaction):
    await interaction.response.send_message("Adding bridge..", ephemeral=True)
    webhook = await interaction.channel.create_webhook(name="Guildcord")
    session = aiohttp.ClientSession()
    await session.post(
        f"https://guildcord-api.tk/update/{interaction.channel.guild.id}?channel_discord={interaction.channel.id}&"
        f"webhook_discord={webhook.url}&token={config.MASTER_TOKEN}")
    await session.close()
    await interaction.edit_original_message(content=
        f"Added new channel. Execute `gc!add-bridge {interaction.guild.id}` on the other side/s.")




@client.slash_command(name="help")
async def help(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Guildcord", description="API Docs: https://guildcord-api.tk")
    embed.add_field(name="register", value="Register you server.", inline=False)
    embed.add_field(name="delete", value="Delete your endpoint.", inline=False)
    embed.add_field(name="generate-token", value="Generate a new token for your endpoint.", inline=False)
    embed.add_field(name="allow", value="Allow a bot or webhook to be forwarded.", inline=False)
    embed.add_field(name="set-log", value="Setup your logchannel.", inline=False)
    embed.add_field(name="add-bridge", value="Add another channel to bridge over.\nNote: Works like `register`", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.slash_command(name="delete", default_member_permissions=8, description="Delete your endpoint.")
async def delete(interaction: nextcord.Interaction):
    await interaction.response.send_message("Deleting your endpoint..", ephemeral=True)
    session = aiohttp.ClientSession()
    await session.delete(
        f"https://guildcord-api.tk/delete/{interaction.guild.id}?token={config.MASTER_TOKEN}")
    await session.close()
    await interaction.edit_original_message(content=f"Deleted your endpoint.", ephemeral=True)


@client.slash_command(name="set-log", default_member_permissions=8, description="Set logs")
async def setlog(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
    await interaction.response.send_message("Setting logchannel..", ephemeral=True)
    session = aiohttp.ClientSession()
    await session.post(
        f"https://guildcord-api.tk/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
        f"&log_discord={channel.id}")
    await session.close()
    await interaction.edit_original_message(content=f"Added {channel.mention} as logchannel.")


@client.slash_command(name="allow", default_member_permissions=8, description="Allow a webhook or bot")
async def allow(interaction: nextcord.Interaction, id):
    await interaction.response.send_message(f"Adding {id} to allowlist..", ephemeral=True)
    session = aiohttp.ClientSession()
    await session.post(
        f"https://guildcord-api.tk/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
        f"&allowed_ids={id}")
    await session.close()
    await interaction.edit_original_message(content=f"Added {id} to allowlist.")


@client.slash_command(name="update", default_member_permissions=8, description="Update your endpoint.")
async def update(interaction: nextcord.Interaction, action=nextcord.SlashOption(
    name="action",
    choices={
        "webhook_discord", "webhook_guilded", "log_discord", "log_guilded", "channel_discord", "channel_guilded"}),
                 *, value):
    await interaction.response.send_message("Updating your endpoint..", ephemeral=True)
    session = aiohttp.ClientSession()
    if action == "webhook_discord":
        await session.post(
            f"https://guildcord-api.tk/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
            f"&webhook_discord={value}")
        await interaction.edit_original_message(content=f"Updated your endpoint.")

    if action == "webhook_guilded":
        await session.post(
            f"https://guildcord-api.tk/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
            f"&webhook_guilded={value}")
        await interaction.edit_original_message(content=f"Updated your endpoint.")
    if action == "log_discord":
        await session.post(
            f"https://guildcord-api.tk/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
            f"&log_discord={value}")
        await interaction.edit_original_message(content=f"Updated your endpoint.")

    if action == "log_guilded":
        await session.post(
            f"https://guildcord-api.tk/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
            f"&log_guilded={value}")
        await interaction.edit_original_message(content=f"Updated your endpoint.")
    if action == "channel_discord":
        await session.post(
            f"https://guildcord-api.tk/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
            f"&channel_discord={value}")
        await interaction.edit_original_message(content=f"Updated your endpoint.")
    if action == "channel_guilded":
        await session.post(
            f"https://guildcord-api.tk/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
            f"&channel_guilded={value}")
        await interaction.edit_original_message(content=f"Updated your endpoint.")
    await session.close()


@client.slash_command(name="generate-token", default_member_permissions=8, description="Generate a new API Token.")
async def gen(interaction: nextcord.Interaction):
    await interaction.response.send_message("Generating token..", ephemeral=True)
    session = aiohttp.ClientSession()
    async with session.post(
            f"https://guildcord-api.tk/token/{interaction.guild.id}?master_token={config.MASTER_TOKEN}") as token_gen:
        token = await token_gen.json()
        await interaction.edit_original_message(content=f"Your new API Token is: `{token['token']}`\n"
                                                f"Save this and **__do not__** share this!")
        await session.close()


client.run(config.DISCORD_TOKEN)
