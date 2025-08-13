from astroidapi import surrealdb_handler
import re
import requests
import aiohttp
import os
import pathlib
import asyncio
import Bot.config as config


async def get_emoji(emoji, endpoint, sender):
    endpoint_data = await surrealdb_handler.get_endpoint(endpoint, __file__)
    if endpoint_data is None:
        return None
    emoji_list = endpoint_data['config']['emojis']

    if sender == "discord":
        for emoji_data in emoji_list:
            if emoji_data[sender] == emoji:
                return emoji_data
    
    elif sender == "guilded":
        for emoji_data in emoji_list:
            if emoji_data[sender] == emoji:
                return emoji_data
    
    elif sender == "nerimity":
        for emoji_data in emoji_list:
            if emoji_data[sender] == emoji:
                print("Found emoji")
                return emoji_data

async def convert_emoji(emoji, sender, receiver, endpoint):
    try:
        emoji_data = await get_emoji(emoji, endpoint, sender)
        if emoji_data is None:
            return None
        return emoji_data[receiver]
    except KeyError:
        return emoji

async def convert_message(message, sender, receiver, endpoint):
    print(message)
    if sender == "discord":
        emojis = re.findall(r'<a?:\w+:\d+>', message) or re.findall(r':\w+:', message)
        print(emojis)
        for emoji in emojis:
            print(emoji)
            emoji_data = await convert_emoji(emoji, sender, receiver, endpoint)
            print(emoji_data)
            if emoji_data is not None:
                message = message.replace(emoji, emoji_data)
            else:
                endpoint_data = await surrealdb_handler.get_endpoint(endpoint, __file__)
                if endpoint_data["config"]["emoji_filtering"]:
                    message = message.replace(emoji, "")
                


    elif sender == "guilded":
        emojis = re.findall(r':\w+:', message)
        print(emojis)
        for emoji in emojis:
            print(emoji)
            emoji_data = await convert_emoji(emoji, sender, receiver, endpoint)
            print(emoji_data)
            if emoji_data is not None:
                message = message.replace(emoji, emoji_data)
            else:    
                endpoint_data = await surrealdb_handler.get_endpoint(endpoint, __file__)
                if endpoint_data["config"]["emoji_filtering"]:
                    message = message.replace(emoji, "")
    
    elif sender == "nerimity":
        emojis = re.findall(r'\[ace:\d+:\w+\]|\[ce:\d+:\w+\]', message)
        print(emojis)
        for emoji in emojis:
            print(emoji)
            emoji_data = await convert_emoji(emoji, sender, receiver, endpoint)
            print(emoji_data)
            if emoji_data is not None:
                message = message.replace(emoji, emoji_data)
            else:    
                endpoint_data = await surrealdb_handler.get_endpoint(endpoint, __file__)
                if endpoint_data["config"]["emoji_filtering"]:
                    message = message.replace(emoji, "")
    
    elif sender == "revolt":
        emojis = re.findall(r':\w+:', message)
        print(emojis)
        for emoji in emojis:
            print(emoji)
            emoji_data = await convert_emoji(emoji, sender, receiver, endpoint)
            print(emoji_data)
            if emoji_data is not None:
                message = message.replace(emoji, emoji_data)
            else:    
                endpoint_data = await surrealdb_handler.get_endpoint(endpoint, __file__)
                if endpoint_data["config"]["emoji_filtering"]:
                    message = message.replace(emoji, "")

    return message


async def get_discord_emojis(endpoint):
    emojis_list = []
    url = f"https://discord.com/api/v9/guilds/{endpoint}/emojis"
    _endpointData = await surrealdb_handler.get_endpoint(endpoint, __file__)
    if _endpointData["config"]["isbeta"] is True:
        headers = {
            "Authorization": f"Bot {config.BETA_DISCORD_TOKEN}"
        }
    else:
        headers = {
            "Authorization": f"Bot {config.DISCORD_TOKEN}"
        }

    response = requests.get(url, headers=headers)
    emojis = response.json()

    for emoji in emojis:
        emoji_id = emoji["id"]
        emoji_name = emoji["name"]
        if emoji["animated"]:
            emoji_asset_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif"
        else:
            emoji_asset_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        emoji_object = {
            "name": emoji_name,
            "id": emoji_id,
            "url": emoji_asset_url
        }
        print(emoji_asset_url)
        emojis_list.append(emoji_object)

    return emojis_list

async def get_corresponding_endpoint(endpoint, platform):    
    if platform == "discord":
        endpoint_data = await surrealdb_handler.GetEndpoint.get_relations(endpoint)
        return endpoint_data
    elif platform == "guilded":
        endpoint_data = await surrealdb_handler.GetEndpoint.from_guilded_id(endpoint)
        endpoint_data = await surrealdb_handler.GetEndpoint.get_relations(endpoint_data["discord"])
        return endpoint_data
    elif platform == "nerimity":
        endpoint_data = await surrealdb_handler.GetEndpoint.from_nerimity_id(endpoint)
        endpoint_data = await surrealdb_handler.GetEndpoint.get_relations(endpoint_data["discord"])
        return endpoint_data
    


async def sync_discord_emojis(endpoint, platform):
    emojis = await get_discord_emojis(endpoint)
    est_time = 0
    for emoji in emojis:
        est_time += 9
    try:
        asyncio.create_task(_sync_discord_emojis(endpoint, platform))
        return {"message": "Emoji synchronization task started. Running in background. Estaimated time: " + str(est_time) + " seconds until completed.", "est_time": est_time}
    except Exception as e:
        return {"message": f"Failed to start emoji synchronization task. Error: {e}"}

async def _sync_discord_emojis(endpoint, platform):
    emojis = await get_discord_emojis(endpoint)
    endpoint_data = await get_corresponding_endpoint(endpoint, platform)

    session = aiohttp.ClientSession()
    
    for emoji in emojis:
        await asyncio.sleep(7)
        if "~" in emoji["name"]:
            emoji["name"] = emoji["name"].split("~")[0]
        else:
            emoji_name = emoji["name"]
        emoji_id = emoji["id"]
        emoji_url = emoji["url"]

        with open(f"{pathlib.Path(__file__).parent.resolve()}/emoji_uploads/{emoji_id}.png", "wb") as file:
            response = requests.get(emoji_url, stream=True)
            file.write(response.content)
            file.close()
            
            emoji = f"{pathlib.Path(__file__).parent.resolve()}/emoji_uploads/{emoji_id}.png"
            formdata = aiohttp.FormData()
            formdata.add_field("f", open(os.path.abspath(emoji), "rb"), filename=f"{emoji_name}.{emoji_url.split('.')[-1]}", content_type=f"image/{emoji_url.split('.')[-1]}")
            
            _endpointData = await surrealdb_handler.get_endpoint(endpoint, __file__)
            log_channel = _endpointData["config"]["logs"]["discord"]
            if _endpointData["config"]["isbeta"] is True:
                log_headers = {
                    "Authorization": f"Bot {config.BETA_DISCORD_TOKEN}"
                }
            else:
                log_headers = {
                    "Authorization": f"Bot {config.DISCORD_TOKEN}"
                }
            send_log_url = f"https://discord.com/api/v9/channels/{log_channel}/messages"
            if _endpointData["config"]["isbeta"] is True:
                headers = {
                    "Authorization": f"{config.BETA_NERIMITY_TOKEN}"
                    }
            else:
                headers = {
                    "Authorization": f"{config.NERIMITY_TOKEN}"
                    }

            async with session.post("https://cdn.nerimity.com/upload", headers=headers, data=formdata) as r:
                try:
                    if r.ok:
                        nerimityCdnFileId = (await r.json())["fileId"]
                        print(f"Uploaded emoji {emoji_name} to nerimity cdn with id {nerimityCdnFileId}")
                        cdnurl = f"https://cdn.nerimity.com/emojis/{nerimityCdnFileId}"
                        r = requests.post(cdnurl)
                        print(r.text)
                        payload = {
                            "name": emoji_name,
                            "fileId": str(nerimityCdnFileId)
                        }
                        print(payload)
                        async with session.post(f"https://nerimity.com/api/servers/{int(endpoint_data['nerimity'])}/emojis", headers=headers, data=payload) as r:
                            if r.ok:
                                print(f"Uploaded emoji {emoji_name} to nerimity")
                                endpoint_emojis = await surrealdb_handler.get_endpoint(int(endpoint), __file__)
                                endpoint_emojis = endpoint_emojis["config"]["emojis"]
                                nerimityEmojiId = (await r.json())["id"]
                                emoji_object = {
                                    "discord": f"<:{emoji_name}:{emoji_id}>",
                                    "nerimity": f"[ce:{nerimityEmojiId}:{emoji_name}]",
                                    "guilded": None,
                                    "revolt": None,
                                }
                                if emoji_url.endswith(".gif"):
                                    emoji_object["discord"] = f"<a:{emoji_name}:{emoji_id}>"
                                    emoji_object["nerimity"] = f"[ace:{nerimityEmojiId}:{emoji_name}]"

                                for emoji in endpoint_emojis:
                                    if f"<:{emoji_name}:" in emoji["discord"] or f"<a:{emoji_name}:" in emoji["discord"]:
                                        emoji_object_index = endpoint_emojis.index(emoji)
                                        p = endpoint_emojis.pop(emoji_object_index)
                                        print(f"Removed emoji {emoji_name} from endpoint {endpoint}")

                                endpoint_emojis.append(emoji_object)
                                await surrealdb_handler.write_to_structure(int(endpoint), "config.emojis", endpoint_emojis)
                                embed = {
                                    "title": "Emoji Added",
                                    "description": f"Added emoji {emoji_name} to endpoint {endpoint}",
                                    "color": 0x00ff00,
                                    "thumbnail": {
                                        "url": emoji_url
                                    }
                                }
                                await session.post(send_log_url, headers=log_headers, json=embed)
                                print(f"Added emoji {emoji_name} to endpoint {endpoint}")
                            else:
                                if emoji_url.endswith(".gif"):
                                    await session.post(send_log_url, headers=log_headers, json={"content": f"Failed to upload emoji <a:{emoji_name}:{emoji_id}> to nerimity. Response from {platform}: {r.status}, {r.reason}"})
                                else:
                                    await session.post(send_log_url, headers=log_headers, json={"content": f"Failed to upload emoji <:{emoji_name}:{emoji_id}> to nerimity. Response from {platform}: {r.status}, {r.reason}"})
                                raise Exception(f"Failed to upload emoji to nerimity. Response: {r.status}, {r.text}")
                    else:
                        raise Exception(f"Failed to emoji attachment to nerimity. Response: {r.status}, {r.reason}")
                except Exception as e:
                    print(f"Failed to upload emoji {emoji_name} to nerimity. Error: {e}")
                    continue
                
    await session.close()
    for emoji in emojis:
        try:
            os.remove(f"{pathlib.Path(__file__).parent.resolve()}/emoji_uploads/{emoji['id']}.png")
            print(f"Deleted emoji file {emoji['id']}.png")
        except Exception as e:
            print(f"Failed to delete emoji file {emoji['id']}.png")
            continue


async def add_emoji(endpoint, emoji):
    endpoint_data = await surrealdb_handler.get_endpoint(int(endpoint), __file__)
    endpoint_emojis = endpoint_data["config"]["emojis"]
    endpoint_emojis.append(emoji)
    await surrealdb_handler.write_to_structure(int(endpoint), "config.emojis", endpoint_emojis)
    return {
                "message": f"Added emoji {emoji} to endpoint {endpoint}"
    }


async def remove_emoji(endpoint, emoji):
    endpoint_data = await surrealdb_handler.get_endpoint(int(endpoint), __file__)
    endpoint_emojis = endpoint_data["config"]["emojis"]
    for emoji_data in endpoint_emojis:
        if "discord" in emoji_data.keys():
            if emoji_data["discord"] == emoji["discord"]:
                endpoint_emojis.remove(endpoint_emojis[endpoint_emojis.index(emoji_data)])
                await surrealdb_handler.write_to_structure(int(endpoint), "config.emojis", endpoint_emojis)
                return {"message": f"Removed emoji {emoji['discord']} from endpoint {endpoint}"}
        if "nerimity" in emoji_data.keys():
            if emoji_data["nerimity"] == emoji["nerimity"]:
                endpoint_emojis.remove(endpoint_emojis[endpoint_emojis.index(emoji_data)])
                await surrealdb_handler.write_to_structure(int(endpoint), "config.emojis", endpoint_emojis)
                return {"message": f"Removed emoji {emoji['nerimity']} from endpoint {endpoint}"}
        if "guilded" in emoji_data.keys():
            if emoji_data["guilded"] == emoji["guilded"]:
                endpoint_emojis.remove(endpoint_emojis[endpoint_emojis.index(emoji_data)])
                await surrealdb_handler.write_to_structure(int(endpoint), "config.emojis", endpoint_emojis)
                return {"message": f"Removed emoji {emoji['guilded']} from endpoint {endpoint}"}
        if "revolt" in emoji_data.keys():
            if emoji_data["revolt"] == emoji["revolt"]:
                endpoint_emojis.remove(endpoint_emojis[endpoint_emojis.index(emoji_data)])
                await surrealdb_handler.write_to_structure(int(endpoint), "config.emojis", endpoint_emojis)
                return {"message": f"Removed emoji {emoji['revolt']} from endpoint {endpoint}"}


async def update_emoji(endpoint, emoji):
    endpoint_data = await surrealdb_handler.get_endpoint(int(endpoint), __file__)
    endpoint_emojis = endpoint_data["config"]["emojis"]
    for emoji_data in endpoint_emojis:
        if "discord" in emoji_data.keys():
            emoji_data["discord"] = emoji["discord"]
        if "nerimity" in emoji_data.keys():
            emoji_data["nerimity"] = emoji["nerimity"]
        if "guilded" in emoji_data.keys():
            emoji_data["guilded"] = emoji["guilded"]
        if "revolt" in emoji_data.keys():
            emoji_data["revolt"] = emoji["revolt"]
    await surrealdb_handler.write_to_structure(int(endpoint), "config.emojis", endpoint_emojis)
    return {"message": f"Updated emoji {emoji['discord']} in endpoint {endpoint}"}
