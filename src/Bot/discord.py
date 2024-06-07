import datetime
import logging
import nextcord
from nextcord.ext import commands
import config
import aiohttp
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

# Set up logging
logger = logging.getLogger('nextcord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='nextcord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Set up intents and create the bot client
intents = nextcord.Intents.all()
client = commands.Bot(command_prefix="gc!", intents=intents)

# Create an aiohttp session
session = aiohttp.ClientSession()

@client.event
async def on_ready():
    await client.sync_all_application_commands()
    print(f"Logged in as {client.user} ({client.user.id})")

# Slash command to send an embed
@client.slash_command(name="send-embed")
async def send_embed(interaction: nextcord.Interaction):
    # Create an embed
    embed = nextcord.Embed(title="Test Title", description="Test Description")
    embed.add_field(name="Test Field", value="Test Field Value")
    embed.set_image(url="https://media1.tenor.com/m/YYPY5tPFIE8AAAAd/bad-teeth.gif")
    embed.set_thumbnail(url="https://media.pinatafarm.com/protected/B183D0EF-49B8-47BF-A523-E72FD0CFFAAC/Soyjak-Pointing.2.meme.webp")
    # Send the embed
    await interaction.channel.send("Test Message", embed=embed)
    await interaction.response.send_message("Embed sent successfully.")

# Event handler for message deletion
@client.event
async def on_message_delete(message: nextcord.Message):
    # Get channel information from the API
    async with session.get(f"https://astroid.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
        channel_json = await channel_request.json()
    if message.channel.id in channel_json["config"]["channels"]["discord"]:
        # Create an embed with deleted message information
        embed = nextcord.Embed(title=f"{message.author.name} - Deleted", description=message.content, colour=0xf5c400)
        embed.add_field(name="Created at", value=f'{datetime.datetime.strftime(message.created_at, "%Y-%m-%d %H:%M:%S")} UTC')
        # Send the embed to the log channel
        async with session.get(f"https://astroid.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}") as log_request:
            log_json = await log_request.json()
        await client.get_channel(log_json["config"]["logs"]["discord"]).send(embed=embed)

# Event handler for message edit
@client.event
async def on_message_edit(before: nextcord.Message, after: nextcord.Message):
    # Get channel information from the API
    async with session.get(f"https://astroid.deutscher775.de/{before.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
        channel_json = await channel_request.json()
    if before.channel.id in channel_json["config"]["channels"]["discord"]:
        # Create an embed with edited message information
        embed = nextcord.Embed(title=f"{before.author.name} - Edited", description=after.content, colour=0xf5c400)
        embed.add_field(name="Jump", value=after.jump_url)
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        # Send the embed to the log channel
        async with session.get(f"https://astroid.deutscher775.de/{before.guild.id}?token={config.MASTER_TOKEN}") as log_request:
            log_json = await log_request.json()
        await client.get_channel(log_json["config"]["logs"]["discord"]).send(embed=embed)


# Event handler for new messages
@client.event
async def on_message(message: nextcord.Message):
    async with session.get(f"https://astroid.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}") as isbeta:
        isbeta = await isbeta.json()
        if isbeta.get("config").get("isbeta"):
            return
    try:
        # Get channel information from the API
        async with session.get(f"https://astroid.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}") as discord_channel_request:
            discord_channel = await discord_channel_request.json()
        if str(message.channel.id) in discord_channel.get("config").get("channels").get("discord"):
            global blacklist
            # Get blacklist information from the API
            async with session.get(f"https://astroid.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}") as blacklist_request:
                blacklist = await blacklist_request.json()
            for word in blacklist.get("config").get("blacklist"):
                if word and word.lower() in message.content.lower():
                    # Create an embed for flagged messages
                    embed = nextcord.Embed(title=f"{message.author.name} - Flagged", description=message.content, colour=0xf5c400)
                    await message.delete()
                    # Get channel information from the API
                    async with session.get(f"https://astroid.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
                        channel = await channel_request.json()
                    # Send the embed to the log channel
                    await client.get_channel(channel.get("config").get("logs").get("discord")).send(embed=embed)
                    return
            global allowed_ids
            # Get allowed IDs information from the API
            try:
                async with session.get(f"https://astroid.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}") as allowed_ids_request:
                    allowed_ids = await allowed_ids_request.json()
            except:
                pass
            if not message.author.bot or str(message.author.id) in allowed_ids.get("config").get("allowed-ids"):
                if not message.attachments and not message.embeds:
                    print(1)
                    # Update the message content in the API
                    async with session.post(f"https://astroid.deutscher775.de/update/{message.channel.guild.id}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}") as update_request:
                        pass
                if message.embeds:
                    print(2)
                    embed = {
                        "title": f"{message.embeds[0].title if message.embeds[0].title else None}",
                        "description": f"{message.embeds[0].description if message.embeds[0].description else None}",
                        "thumbnail": f"{message.embeds[0].thumbnail.url if message.embeds[0].thumbnail.url else None}",
                        "image": f"{message.embeds[0].image.url if message.embeds[0].image else None}",
                        "footer": f"{message.embeds[0].footer.text if message.embeds[0].footer.text else None}",
                        "fields" : []
                    }
                    if message.embeds[0].fields:
                        for field in message.embeds[0].fields:
                            embed["fields"].append({"name": field.name, "value": field.value, "inline": str(field.inline).lower()})
                    # Update the message content with embed in the API
                    async with session.post(f"https://astroid.deutscher775.de/update/{message.channel.guild.id}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_embed={embed}") as update_request:
                        pass
                if message.attachments:
                    print(3)
                    if len(message.attachments) == 1:
                        # Update the message content with attachment in the API
                        async with session.post(f"https://astroid.deutscher775.de/update/{message.channel.guild.id}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_attachments={message.attachments[0].url}") as update_request:
                            pass
                    else:
                        attachments = ""
                        for attachment in message.attachments:
                            attachments += attachment.url
                        # Update the message content with multiple attachments in the API
                        async with session.post(f"https://astroid.deutscher775.de/update/{message.channel.guild.id}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_attachments={attachments[:-1]}") as update_request:
                            pass
    except KeyError:
        pass
    except:
        traceback.print_exc()
        pass


# Slash command to activate beta mode
@client.slash_command(name="activate_beta", description="Activate beta mode")
async def activate_beta(interaction: nextcord.Interaction):
    await interaction.response.send_message("Activating beta mode..", ephemeral=True)
    # Update the beta status in the API
    async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&beta=true") as r:
        if r.ok:
            await interaction.edit_original_message(content="Activated beta mode.")
        else:
            await interaction.edit_original_message(content=r.json().get("message"))

# Slash command to register the server
@client.slash_command(name="register", default_member_permissions=8, description="Automatically register your server.")
async def register(interaction: nextcord.Interaction):
    await interaction.response.send_message("Starting registering process.. (This may take a while.)", ephemeral=True)
    try:
        # Create a webhook for astroid
        webhook = await interaction.channel.create_webhook(name="astroid")
        # Create an endpoint in the API
        async with session.post(f"https://astroid.deutscher775.de/create?endpoint={interaction.guild.id}") as r1:
            if r1.ok:
                await interaction.edit_original_message(content="Created endpoint. Updating values.. (This may take a while.)")
            else:
                await interaction.edit_original_message(content=r1.json().get("message"))
        # Request a token from the API
        async with session.post(f"https://astroid.deutscher775.de/token/{interaction.guild.id}?master_token={config.MASTER_TOKEN}") as token_request:
            token_data = await token_request.json()
        token = token_data["token"]
        # Update values in the API
        async with session.post(f"https://astroid.deutscher775.de/update/{interaction.channel.guild.id}?channel_discord={interaction.channel_id}&webhook_discord={webhook.url}&token={config.MASTER_TOKEN}") as r2:
            if r2.ok:    
                await interaction.edit_original_message(content="Updated values. Requesting token.. (This may take a while.)")
            else:    
                await interaction.edit_original_message(content=r2.json().get("message"))
        if token_request.ok:
            await interaction.edit_original_message(content=f"Created enpoint: https://astroid.deutscher775.de/{interaction.guild.id}\nYour API Token is: `{token}`\nSave this and **__do not__** share this!\nHop over to Guilded and run this command in the channel, you want do bridge over:`gc!register {interaction.guild.id}`")
        else:
            await interaction.edit_original_message(content=token_data.get("message"))    
    except:
        traceback.print_exc()

# Slash command to add another channel for bridging
@client.slash_command(name="add-bridge", description="Add another channel for bridging")
async def add_bridge(interaction: nextcord.Interaction):
    await interaction.response.send_message("Adding bridge..", ephemeral=True)
    # Create a webhook for astroid
    webhook = await interaction.channel.create_webhook(name="astroid")
    # Update values in the API
    async with session.post(f"https://astroid.deutscher775.de/update/{interaction.channel.guild.id}?channel_discord={interaction.channel_id}&webhook_discord={webhook.url}&token={config.MASTER_TOKEN}") as r:
        if r.ok:
            await interaction.edit_original_message(content=f"Added new channel. Execute `gc!add-bridge {interaction.guild.id}` on the other side/s.")
        else:
            await interaction.edit_original_message(content=r.json().get("message"))

# Slash command to display help information
@client.slash_command(name="help")
async def help(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="astroid", description="API Docs: https://astroid.deutscher775.de")
    embed.add_field(name="register", value="Register you server.", inline=False)
    embed.add_field(name="delete", value="Delete your endpoint.", inline=False)
    embed.add_field(name="generate-token", value="Generate a new token for your endpoint.", inline=False)
    embed.add_field(name="allow", value="Allow a bot or webhook to be forwarded.", inline=False)
    embed.add_field(name="set-log", value="Setup your logchannel.", inline=False)
    embed.add_field(name="add-bridge", value="Add another channel to bridge over.\nNote: Works like `register`", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Slash command to delete the endpoint
@client.slash_command(name="delete", default_member_permissions=8, description="Delete your endpoint.")
async def delete(interaction: nextcord.Interaction):
    await interaction.response.send_message("Deleting your endpoint..", ephemeral=True)
    # Delete the endpoint in the API
    async with session.delete(f"https://astroid.deutscher775.de/delete/{interaction.guild.id}?token={config.MASTER_TOKEN}") as r:
        if r.ok:    
            await interaction.edit_original_message(content="Deleted endpoint.")
        else:    
            await interaction.edit_original_message(content=await r.json().get("message"))

# Slash command to set the log channel
@client.slash_command(name="set-log", default_member_permissions=8, description="Set logs")
async def setlog(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
    await interaction.response.send_message("Setting logchannel..", ephemeral=True)
    # Update the log channel in the API
    async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&log_discord={channel.id}") as r:
        if r.ok:    
            await interaction.edit_original_message(content="Set logchannel.")
        else:    
            await interaction.edit_original_message(content=r.json().get("message"))

# Slash command to allow a webhook or bot
@client.slash_command(name="allow", default_member_permissions=8, description="Allow a webhook or bot")
async def allow(interaction: nextcord.Interaction, id):
    await interaction.response.send_message(f"Adding {id} to allowlist..", ephemeral=True)
    # Update the allowed IDs in the API
    async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&allowed_ids={id}") as r:
        if r.ok:    
            await interaction.edit_original_message(content=f"Added {id} to allowlist.")
        else:    
            await interaction.edit_original_message(content=r.json().get("message"))

# Slash command to update the endpoint
@client.slash_command(name="update", default_member_permissions=8, description="Update your endpoint.")
async def update(interaction: nextcord.Interaction, action=nextcord.SlashOption(name="action", choices={"webhook_discord", "webhook_guilded", "log_discord", "log_guilded", "channel_discord", "channel_guilded"}), *, value):
    await interaction.response.send_message("Updating your endpoint..", ephemeral=True)
    if action == "webhook_discord":
        # Update the Discord webhook in the API
        async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&webhook_discord={value}") as r:
            pass
    if action == "webhook_guilded":
        # Update the Guilded webhook in the API
        async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&webhook_guilded={value}") as r:
            pass
    if action == "log_discord":
        # Update the Discord log channel in the API
        async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&log_discord={value}") as r:
            pass
    if action == "log_guilded":
        # Update the Guilded log channel in the API
        async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&log_guilded={value}") as r:
            pass
    if action == "channel_discord":
        # Update the Discord channel in the API
        async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&channel_discord={value}") as r:
            pass
    if action == "channel_guilded":
        # Update the Guilded channel in the API
        async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&channel_guilded={value}") as r:
            pass

# Slash command to generate a new API token
@client.slash_command(name="generate-token", default_member_permissions=8, description="Generate a new API Token.")
async def gen(interaction: nextcord.Interaction):
    await interaction.response.send_message("Generating token..", ephemeral=True)
    # Request a new token from the API
    async with session.post(f"https://astroid.deutscher775.de/token/{interaction.guild.id}?master_token={config.MASTER_TOKEN}") as token_gen:
        token = await token_gen.json()
    if token_gen.ok:
        await interaction.edit_original_message(content=f"Your new API Token is: `{token['token']}`\nSave this and **__do not__** share this!")
    else:
        await interaction.edit_original_message(content=token_gen.get("message"))

@client.slash_command(name="remove-bridge", description="Remove a bridge")
async def remove_bridge(interaction: nextcord.Interaction):
    await interaction.response.send_message("Removing bridge..", ephemeral=True)
    # Update the channel in the API
    async with session.post(f"https://astroid.deutscher775.de/update/{interaction.guild.id}?channel_discord={interaction.channel_id}&token={config.MASTER_TOKEN}") as r:
        if r.ok:    
            await interaction.edit_original_message(content="Removed bridge.")
        else:    
            await interaction.edit_original_message(content=r.json().get("message"))

# Run the bot
client.run(config.DISCORD_TOKEN, reconnect=True)
