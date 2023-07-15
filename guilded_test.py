import guilded
import Bot.config
from guilded.ext import commands

client = commands.Bot(command_prefix="gc!")


@client.event
async def on_ready():
    channel = await client.fetch_channel("132cf366-377c-420d-8f84-355cfb1b03e6")
    await channel.send("Hallo")

client.run(Bot.config.GUILDED_TOKEN)