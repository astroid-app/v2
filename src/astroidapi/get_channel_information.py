from Bot import config
from astroidapi import beta_config
import aiohttp
import asyncio
import traceback


class GetChannelName:

    @classmethod
    async def from_discord_id(cls, channel_id: int):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bot {config.DISCORD_TOKEN}"
                }
                async with session.get(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers) as resp:
                    data = await resp.json()
                    return data["name"]
        except:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bot {beta_config.DISCORD_TOKEN}"
                    }
                    async with session.get(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers) as resp:
                        data = await resp.json()
                        return data["name"]
            except:
                traceback.print_exc()
                return None
                
    
    @classmethod
    async def from_guilded_id(cls, channel_id: str):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {config.GUILDED_TOKEN}"
                }
                async with session.get(f"https://www.guilded.gg/api/v1/channels/{channel_id}", headers=headers) as resp:
                    print(await resp.text())
                    data = await resp.json()
                    return data["channel"]["name"]
        except:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {beta_config.GUILDED_TOKEN}"
                    }
                    async with session.get(f"https://www.guilded.gg/api/v1/channels/{channel_id}", headers=headers) as resp:
                        print(await resp.text())
                        data = await resp.json()
                        return data["channel"]["name"]
            except:
                return None
        
    
    @classmethod
    async def from_revolt_id(cls, channel_id: str):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "X-Session-Token": f"{config.REVOLT_TOKEN}"
                }
                async with session.get(f"https://api.revolt.chat/channels/{channel_id}", headers=headers) as resp:
                    print(await resp.text())
                    data = await resp.json()
                    return data["name"]
        except:
            
            return None
    
    @classmethod
    async def from_nerimity_id(cls, channel_id: int):
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": config.NERIMITY_TOKEN
                }
                async with session.get(f"https://nerimity.com/api/channels/{channel_id}", headers=headers) as resp:
                    print(await resp.text())
                    data = await resp.json()
                    return data["name"]
        except:
            traceback.print_exc()
            return None