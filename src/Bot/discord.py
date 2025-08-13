import datetime
import logging
import nextcord
from nextcord.ext import commands
import config
import aiohttp
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

# Set up logging
logger = logging.getLogger('nextcord')
logger.setLevel(logging.DEBUG)
date = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
handler = logging.FileHandler(filename=f'nextcord-{date}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Set up intents and create the bot client
intents = nextcord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# Create an aiohttp session
session = aiohttp.ClientSession()

async def send_iamup():
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://status.astroid.cc/monitor/iamup/discord") as r:
            await session.close()
            if r.status == 200:
                print("Sent up status.")
            else:
                print("Could not send up status.")


async def iamup_loop():
    while True:
        asyncio.create_task(send_iamup())
        await asyncio.sleep(40)

async def activity_task():
    while True:
        print("Updating activity..")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.astroid.cc/statistics") as r:
                data = await r.json()
                await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=f'{data["messages"]["total_rounded"]}+ messages | {data["endpoints"]} registered servers'))
                print("Updated activity.")
        await asyncio.sleep(120)


@client.event
async def on_ready():
    await client.sync_all_application_commands()
    print(f"Logged in as {client.user} ({client.user.id})")
    client.loop.create_task(iamup_loop())
    client.loop.create_task(activity_task())
    #while True:
    #    async with aiohttp.ClientSession() as session:
    #        async with session.post(f"https://status.astroid.cc//monitor/iamup/discord") as r:
    #            if r.status == 200:
    #                print("Sent up status.")
    #            else:
    #                print("Could not send up status.")
    #    await asyncio.sleep(10)

# Event handler for message edit
@client.event
async def on_message_edit(before: nextcord.Message, after: nextcord.Message):
    # Get channel information from the API
    async with session.get(f"https://api.astroid.cc/{before.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
        channel_json = await channel_request.json()
        if str(before.channel.id) in channel_json["config"]["channels"]["discord"]:
            # Create an embed with edited message information
            embed = nextcord.Embed(title=f"{before.author.name} - Edited", description=after.content, colour=0xf5c400)
            embed.add_field(name="Jump", value=after.jump_url)
            embed.add_field(name="Before", value=before.content, inline=False)
            embed.add_field(name="After", value=after.content, inline=False)
            # Send the embed to the log channel
            async with session.get(f"https://api.astroid.cc/{before.guild.id}?token={config.MASTER_TOKEN}") as log_request:
                log_json = await log_request.json()
            await client.get_channel(int(log_json["config"]["logs"]["discord"])).send(embed=embed)


# Event handler for new messages
@client.event
async def on_message(message: nextcord.Message):
    async with session.get(f"https://api.astroid.cc/{message.guild.id}?token={config.MASTER_TOKEN}") as isbeta:
        isbeta = await isbeta.json()
        if isbeta.get("config").get("isbeta"):
            return
    try:
        # Get channel information from the API
        async with session.get(f"https://api.astroid.cc/{message.guild.id}?token={config.MASTER_TOKEN}") as discord_channel_request:
            discord_channel = await discord_channel_request.json()
        if str(message.channel.id) in discord_channel.get("config").get("channels").get("discord"):
            async with session.get(f"https://api.astroid.cc/optout/{message.author.id}?token={config.MASTER_TOKEN}") as optout_request:
                optout = await optout_request.json()
            if optout.get("optedOut"):
                return
            
            global blacklist
            # Get blacklist information from the API
            async with session.get(f"https://api.astroid.cc/{message.guild.id}?token={config.MASTER_TOKEN}") as blacklist_request:
                blacklist = await blacklist_request.json()
            for word in blacklist.get("config").get("blacklist"):
                if word and word.lower() in message.content.lower():
                    # Create an embed for flagged messages
                    embed = nextcord.Embed(title=f"{message.author.name} - Flagged", description=message.content, colour=0xf5c400)
                    await message.delete()
                    # Get channel information from the API
                    async with session.get(f"https://api.astroid.cc/{message.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
                        channel = await channel_request.json()
                    # Send the embed to the log channel
                    await client.get_channel(channel.get("config").get("logs").get("discord")).send(embed=embed)
                    return
            global allowed_ids
            # Get allowed IDs information from the API
            try:
                async with session.get(f"https://api.astroid.cc/{message.guild.id}?token={config.MASTER_TOKEN}") as allowed_ids_request:
                    allowed_ids = await allowed_ids_request.json()
            except:
                pass
            if not message.author.bot or str(message.author.id) in allowed_ids.get("config").get("allowed-ids"):
                if not message.attachments and not message.embeds:
                    print(1)
                    # Update the message content in the API
                    async with session.post(f"https://api.astroid.cc/update/{message.channel.guild.id}?message_content={message.content}&message_author_name={message.author.display_name}&message_author_avatar={message.author.avatar.url}&message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}") as update_request:
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
                    async with session.post(f"https://api.astroid.cc/update/{message.channel.guild.id}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url if message.author.avatar.url else 'https://api.astroid.cc/assets/Astroid PFP not found.png'}&message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_embed={embed}") as update_request:
                        pass
                if message.attachments:
                    print(3) 
                    if len(message.attachments) == 1:
                        print(message.attachments[0].url)
                        # Update the message content with attachment in the API
                        async with session.post(f"https://api.astroid.cc/update/{message.channel.guild.id}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url if message.author.avatar.url else 'https://api.astroid.cc/assets/Astroid PFP not found.png'}&message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_attachments={message.attachments[0].url.replace('&', '%26')}") as update_request:
                            pass
                    else:
                        attachments = ""
                        for attachment in message.attachments:
                            attachments += attachment.url
                        # Update the message content with multiple attachments in the API
                        async with session.post(f"https://api.astroid.cc/update/{message.channel.guild.id}?message_content={message.content}&message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url if message.author.avatar.url else 'https://api.astroid.cc/assets/Astroid PFP not found.png'}&message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}&sender_channel={message.channel.id}&message_attachments={attachments[:-1].replace('&', '%26')}") as update_request:
                            pass
    except KeyError:
        pass
    except:
        traceback.print_exc()
        pass


# Event handler for message deletion
@client.event
async def on_message_delete(message: nextcord.Message):
    async with session.get(f"https://api.astroid.cc/{message.guild.id}?token={config.MASTER_TOKEN}") as isbeta:
        isbeta = await isbeta.json()
        if isbeta.get("config").get("isbeta"):
            return
    # Get channel information from the API
    async with session.get(f"https://api.astroid.cc/{message.guild.id}?token={config.MASTER_TOKEN}") as channel_request:
        channel_json = await channel_request.json()
        if str(message.channel.id) in channel_json["config"]["channels"]["discord"]:
            # Create an embed with deleted message information
            embed = nextcord.Embed(title=f"{message.author.name} - Deleted", description=message.content, colour=0xf5c400)
            embed.add_field(name="Created at", value=f'{datetime.datetime.strftime(message.created_at, "%Y-%m-%d %H:%M:%S")} UTC')
            # Send the embed to the log channel
            async with session.get(f"https://api.astroid.cc/{message.guild.id}?token={config.MASTER_TOKEN}") as log_request:
                log_json = await log_request.json()
            await client.get_channel(int(log_json["config"]["logs"]["discord"])).send(embed=embed)


@client.slash_command(name="opt", description="Set your opt-status", force_global=True)
async def opt(interaction: nextcord.Interaction, status: str):
    pass

@opt.subcommand(name="in", description="Opt into Astroid to let your messages be bridged")
async def opt_in(o_interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Opting in?", description="If you opt into Astroid __your messages will be bridged to bridged__ servers.\nThis is global for **all servers** using Astroid.", color=0x3D60FF)
    class ExternalLinkBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.link, label="Privacy", url="https://astroid.cc/privacy")
    
    class ConfirmBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.success, label="Confirm", custom_id="opt_in", emoji="✅")

        async def callback(self, interaction: nextcord.Interaction):
            async with session.post(f"https://api.astroid.cc/optin/{interaction.user.id}?token={config.MASTER_TOKEN}") as r:
                r_json = await r.json()
                if r_json["optedOut"] == False:
                    await interaction.response.send_message("Opted in successfully.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Could not opt in. ({r.status, r.reason})", ephemeral=True)

    class CancelBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.danger, label="Cancel", custom_id="opt_cancel", emoji="❌")

        async def callback(self, interaction: nextcord.Interaction):
            await o_interaction.delete_original_message()
            await interaction.response.send_message("Cancelled.", ephemeral=True)

    class Buttons(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(ExternalLinkBtn())
            self.add_item(ConfirmBtn())
            self.add_item(CancelBtn())
    
    await o_interaction.response.send_message(embed=embed, view=Buttons(), ephemeral=True)


@opt.subcommand(name="out", description="Opt out of Astroid to stop your messages from being bridged")
async def opt_out(o_interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Opting out?", description="If you opt out of Astroid __your messages will not be bridged__ to bridged servers.\nThis is global for **all servers** using Astroid.", color=0x3D60FF)
    class ExternalLinkBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.link, label="Privacy", url="https://astroid.cc/privacy")
    
    class ConfirmBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.success, label="Confirm", custom_id="opt_out", emoji="✅")

        async def callback(self, interaction: nextcord.Interaction):
            async with session.post(f"https://api.astroid.cc/optout/{interaction.user.id}?token={config.MASTER_TOKEN}") as r:
                r_json = await r.json()
                if r_json["optedOut"] == True:
                    await interaction.response.send_message("Opted out successfully.", ephemeral=True)
                else:
                    await interaction.response.send_message(f"Could not opt out. ({r.status, r.reason})", ephemeral=True)
    
    class CancelBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.danger, label="Cancel", custom_id="opt_cancel", emoji="❌")

        async def callback(self, interaction: nextcord.Interaction):
            await o_interaction.delete_original_message()
            await interaction.response.send_message("Cancelled.", ephemeral=True)
    
    class Buttons(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(ExternalLinkBtn())
            self.add_item(ConfirmBtn())
            self.add_item(CancelBtn())
    
    await o_interaction.response.send_message(embed=embed, view=Buttons(), ephemeral=True)

# Slash command to register the server
@client.slash_command(name="register", default_member_permissions=8, description="Welcome! You are one step away from bridging your server", force_global=True)
async def register(interaction: nextcord.Interaction):
    terms_and_privacy_embed = nextcord.Embed(title="Terms and Privacy", description="Please read and accept the terms and privacy policy to continue.", color=0x3D60FF)
    
    async def proceed_with_registration(interaction: nextcord.Interaction):
        """Proceed with the actual registration process"""
        try:
            await interaction.response.send_message("Creating your endpoint...", ephemeral=True)
            
            # Create a webhook for astroid
            webhook = await interaction.channel.create_webhook(name="astroid")
            # Create an endpoint in the API
            async with session.post(f"https://api.astroid.cc/create?endpoint={interaction.guild.id}") as r1:
                if r1.ok:
                    await interaction.edit_original_message(content="Created endpoint. Updating values.. (This may take a while.)")
                else:
                    await interaction.edit_original_message(content=(await r1.json()).get("message"))
            # Request a token from the API
            async with session.post(f"https://api.astroid.cc/token/{interaction.guild.id}?master_token={config.MASTER_TOKEN}") as token_request:
                token_data = await token_request.json()
            token = token_data["token"]
            # Update values in the API
            async with session.post(f"https://api.astroid.cc/update/{interaction.channel.guild.id}?channel_discord={interaction.channel_id}&webhook_discord={webhook.url}&token={config.MASTER_TOKEN}") as r2:
                if r2.ok:    
                    await interaction.edit_original_message(content="Updated values. Requesting token.. (This may take a while.)")
                else:    
                    await interaction.edit_original_message(content=(await r2.json()).get("message"))
            if token_request.ok:
                await interaction.edit_original_message(content=f"Created endpoint: https://api.astroid.cc/{interaction.guild.id}\nYour API Token is: `{token}`\nSave and **__do not__** share this!\nHop over to the other platform/s and run this command in the channel, you want do bridge over to:`a!register {interaction.guild.id}`")
            else:
                await interaction.edit_original_message(content=token_data.get("message"))    
        except Exception:
            traceback.print_exc()
    
    class AcceptBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.success, label="Accept", custom_id="accept_terms", emoji="✅")
        
        async def callback(self, btn_interaction: nextcord.Interaction):
            await proceed_with_registration(btn_interaction)
    
    class DeclineBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.danger, label="Decline", custom_id="decline_terms", emoji="❌")
        
        async def callback(self, btn_interaction: nextcord.Interaction):
            await btn_interaction.response.send_message("You declined the terms and privacy policy. Registration cancelled.", ephemeral=True)
            await interaction.delete_original_message(delay=5)
    
    class ExternalLinksView(nextcord.ui.View):
        def __init__(self):
            super().__init__(timeout=300)  # 5 minute timeout
            self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, label="Terms", url="https://astroid.cc/terms"))
            self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, label="Privacy", url="https://astroid.cc/privacy"))
            self.add_item(nextcord.ui.Button(style=nextcord.ButtonStyle.link, label="User Guide", url="https://docs.astroid.cc"))
            self.add_item(AcceptBtn())
            self.add_item(DeclineBtn())
        
        async def on_timeout(self):
            await interaction.edit_original_message(content="You took too long to respond. Please run the command again.", view=None)

    await interaction.response.send_message(embed=terms_and_privacy_embed, view=ExternalLinksView(), ephemeral=True)

# Slash command to add another channel for bridging
@client.slash_command(name="add-bridge", description="More than one channel huh? Add more with this command", default_member_permissions=8, force_global=True)
async def add_bridge(interaction: nextcord.Interaction):
    await interaction.response.send_message("Adding bridge..", ephemeral=True)
    # Create a webhook for astroid
    webhook = await interaction.channel.create_webhook(name="astroid")
    # Update values in the API
    async with session.post(f"https://api.astroid.cc/update/{interaction.channel.guild.id}?channel_discord={interaction.channel_id}&webhook_discord={webhook.url}&token={config.MASTER_TOKEN}") as r:
        if r.ok:
            await interaction.edit_original_message(content=f"Added new channel. Execute `a!add-bridge {interaction.guild.id}` on the other side/s.")
        else:
            await interaction.edit_original_message(content=r.json().get("message"))

# Slash command to display help information
@client.slash_command(name="help", description="Help needed? This command will show you all the commands available", force_global=True)
async def help(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Astroid", description="First time here? To get started we recommend you our **User Guide: https://docs.astroid.cc ** \n\nTo use any of the command below you need **Administrator permissions**.", color=0x3D60FF)
    class UserGuideExternalLinkBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.link, label="User Guide", url="https://docs.astroid.cc")
    
    class TermsExternalLinkBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.link, label="Terms of Service", url="https://astroid.cc/terms")
    
    class PrivacyExternalLinkBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.link, label="Privacy Policy", url="https://astroid.cc/privacy")

    class ExternalLink(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(UserGuideExternalLinkBtn())
            self.add_item(TermsExternalLinkBtn())
            self.add_item(PrivacyExternalLinkBtn())


    view = ExternalLink()
    embed.add_field(name="register", value="Register you server.", inline=False)
    embed.add_field(name="delete", value="Delete your endpoint.", inline=False)
    embed.add_field(name="generate-token", value="Generate a new token for your endpoint.", inline=False)
    embed.add_field(name="allow", value="Allow a bot or webhook to be forwarded.", inline=False)
    embed.add_field(name="set-log", value="Setup your logchannel.", inline=False)
    embed.add_field(name="add-bridge", value="Add another channel to bridge over.\nNote: Works like `register`", inline=False)
    embed.add_field(name="opt", value="Set your opt-status. This is globally set for **all servers** using Astroid. Changable anytime.\n" \
                        "**in**: Opt into Astroid to allow your messages being bridged.\n" \
                        "**out**: opt out of Astroid. None of you messages will be picked up.", inline=False)
    await interaction.response.send_message(embed=embed, view=view)

# Slash command to delete the endpoint
@client.slash_command(name="delete", default_member_permissions=8, description="You want to delete your endpoint? This command will do it for you.", force_global=True)
async def delete(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Are you sure?", description="This action is irreversible. Are you sure you want to delete your endpoint?", color=0x3D60FF)
    class ConfirmBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.success, label="Confirm", custom_id="delete_confirm", emoji="🗑️")

        async def callback(self, interaction: nextcord.Interaction):
            await interaction.response.send_message("Deleting your endpoint..", ephemeral=True)
            # Delete the endpoint in the API
            async with session.delete(f"https://api.astroid.cc/delete/{interaction.guild.id}?token={config.MASTER_TOKEN}") as r:
                if r.ok:    
                    await interaction.edit_original_message(content="Deleted endpoint.")
                else:    
                    await interaction.edit_original_message(content=await r.json().get("message"))
    class CancelBtn(nextcord.ui.Button):
        def __init__(self):
            super().__init__(style=nextcord.ButtonStyle.danger, label="Cancel", custom_id="delete_cancel", emoji="❌")

        async def callback(self, interaction: nextcord.Interaction):
            await interaction.response.send_message("Cancelled.", ephemeral=True)
    
    class Buttons(nextcord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(ConfirmBtn())
            self.add_item(CancelBtn())

    await interaction.response.send_message(embed=embed, view=Buttons(), ephemeral=True)

# Slash command to set the log channel
@client.slash_command(name="set-log", default_member_permissions=8, description="Messages will be logged in this channel", force_global=True)
async def setlog(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
    await interaction.response.send_message("Setting logchannel..", ephemeral=True)
    # Update the log channel in the API
    async with session.post(f"https://api.astroid.cc/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&log_discord={channel.id}") as r:
        if r.ok:    
            await interaction.edit_original_message(content="Set logchannel.")
        else:    
            await interaction.edit_original_message(content=r.json().get("message"))

# Slash command to allow a webhook or bot
@client.slash_command(name="allow", default_member_permissions=8, description="Allow a webhook or bot to be forwarded", force_global=True)
async def allow(interaction: nextcord.Interaction, id):
    await interaction.response.send_message(f"Adding {id} to allowlist..", ephemeral=True)
    # Update the allowed IDs in the API
    async with session.post(f"https://api.astroid.cc/update/{interaction.guild.id}?token={config.MASTER_TOKEN}&allowed_ids={id}") as r:
        if r.ok:    
            await interaction.edit_original_message(content=f"Added {id} to allowlist.")
        else:    
            await interaction.edit_original_message(content=r.json().get("message"))

# Slash command to generate a new API token
@client.slash_command(name="generate-token", default_member_permissions=8, description="Lost, forgot or leaked your token? Generate a new one", force_global=True)
async def gen(interaction: nextcord.Interaction):
    await interaction.response.send_message("Generating token..", ephemeral=True)
    # Request a new token from the API
    async with session.post(f"https://api.astroid.cc/token/{interaction.guild.id}?master_token={config.MASTER_TOKEN}") as token_gen:
        token = await token_gen.json()
    if token_gen.ok:
        await interaction.edit_original_message(content=f"Your new API Token is: `{token['token']}`\nSave and **__do not__** share this!")
    else:
        await interaction.edit_original_message(content=token_gen.get("message"))

# Run the bot
client.run(config.DISCORD_TOKEN, reconnect=True)
