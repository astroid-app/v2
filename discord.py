import datetime

import nextcord
from nextcord.ext import commands
import config
import requests

client = commands.Bot(command_prefix="gc!", intents=nextcord.Intents.all())


@client.event
async def on_message_delete(message: nextcord.Message):
    if message.channel.id == \
            requests.get(f"http://api.guildcord.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}").json()[
                "config"]["channels"]["discord"]:
        embed = nextcord.Embed(title=f"{message.author.name} - Deleted", description=message.content, colour=0xf5c400)
        embed.add_field(name="Created at",
                        value=f'{datetime.datetime.strftime(message.created_at, "%Y-%m-%d %H:%M:%S")} UTC')
        await client.get_channel(
            requests.get(f"http://api.guildcord.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}").json()[
                "config"]["logs"][
                "discord"]).send(embed=embed)


@client.event
async def on_message_edit(before: nextcord.Message, after: nextcord.Message):
    if before.channel.id == \
            requests.get(f"http://api.guildcord.deutscher775.de/{before.guild.id}?token={config.MASTER_TOKEN}").json()[
                "config"]["channels"]["discord"]:
        embed = nextcord.Embed(title=f"{before.author.name} - Edited", description=after.content, colour=0xf5c400)
        embed.add_field(name="Jump", value=after.jump_url)
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)

        await client.get_channel(
            requests.get(f"http://api.guildcord.deutscher775.de/{before.guild.id}?token={config.MASTER_TOKEN}").json()[
                "config"]["logs"][
                "discord"]).send(embed=embed)


@client.event
async def on_message(message: nextcord.Message):
    try:
        if message.channel.id == requests.get(
                f"http://api.guildcord.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}").json()[
            "config"]["channels"][
            "discord"]:
            blacklist = \
            requests.get(f"http://api.guildcord.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}").json()[
                "config"]["blacklist"]
            for word in blacklist:
                if word is not None:
                    if word.lower() in message.content.lower():
                        embed = nextcord.Embed(title=f"{message.author.name} - Flagged", description=message.content,
                                               colour=0xf5c400)
                        await client.get_channel(requests.get(
                            f"http://api.guildcord.deutscher775.de/{message.guild.id}?token={config.MASTER_TOKEN}").json()[
                                                     "config"]["logs"][
                                                     "discord"]).send(embed=embed)
                        return
                    else:
                        pass
            else:
                if not message.author.bot:
                    if not message.attachments:
                        requests.post(
                            f"http://api.guildcord.deutscher775.de/update/{message.channel.guild.id}?message_content={message.content}&"
                            f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                            f"message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}")
                    if message.attachments:
                        requests.post(
                            f"http://api.guildcord.deutscher775.de/update/{message.channel.guild.id}?message_content={message.content}&"
                            f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                            f"message_author_id={message.author.id}&trigger=true&sender=discord&token={config.MASTER_TOKEN}")

    except requests.exceptions.JSONDecodeError:
        pass


@client.slash_command(name="register", default_member_permissions=8, description="Automatically register your server.")
async def register(interaction: nextcord.Interaction):
    webhook = await interaction.channel.create_webhook(name="Guildcord")
    requests.post(f"http://api.guildcord.deutscher775.de/create?endpoint={interaction.guild.id}")
    requests.post(
        f"http://api.guildcord.deutscher775.de/update/{interaction.channel.guild.id}?channel_discord={interaction.channel.id}&"
        f"webhook_discord={webhook.url}&token={config.MASTER_TOKEN}")
    token = requests.post(
        f"http://api.guildcord.deutscher775.de/token/{interaction.guild.id}?master_token={config.MASTER_TOKEN}")
    await interaction.response.send_message(
        f"Created enpoint: http://api.guildcord.deutscher775.de/{interaction.guild.id}\n"
        f"Your API Token is: `{token.json()['token']}`\n"
        f"Save this and **__do not__** share this!\n"
        f"Hop over to Guilded and run this command in the channel, you want do bridge over:"
        f"`gc!register {interaction.guild.id}`", ephemeral=True)


@client.slash_command(name="help")
async def help(interaction: nextcord.Interaction):
    embed = nextcord.Embed(title="Guildcord", description="API Docs: http://api.guildcord.deutscher775.de")
    embed.add_field(name="register", value="Register you server.", inline=False)
    embed.add_field(name="delete", value="Delete your endpoint.", inline=False)
    embed.add_field(name="generate-token", value="Generate a new token for your endpoint.", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.slash_command(name="delete", default_member_permissions=8, description="Delete your endpoint.")
async def delete(interaction: nextcord.Interaction):
    requests.delete(f"http://api.guildcord.deutscher775.de/delete/{interaction.guild.id}?token={config.MASTER_TOKEN}")
    await interaction.response.send_message(f"Deleted your endpoint.", ephemeral=True)


@client.slash_command(name="set-log", default_member_permissions=8, description="Set logs")
async def setlog(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
    requests.post(f"http://api.guildcord.deutscher775.de/update/{interaction.guild.id}?token={config.MASTER_TOKEN}"
                  f"&log_discord={channel.id}")
    await interaction.response.send_message(f"Updated your endpoint.", ephemeral=True)


@client.slash_command(name="generate-token", default_member_permissions=8, description="Generate a new API Token.")
async def gen(interaction: nextcord.Interaction):
    token = requests.post(
        f"http://api.guildcord.deutscher775.de/token/{interaction.guild.id}?master_token={config.MASTER_TOKEN}")
    await interaction.response.send_message(f"Your new API Token is: `{token.json()['token']}`\n"
                                            f"Save this and **__do not__** share this!", ephemeral=True)


client.run(config.DISCORD_TOKEN)
