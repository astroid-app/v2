from surrealdb import Surreal
import os
import json
from Bot import config
import astroidapi.errors as errors
import traceback
import pathlib
import random
import string
import datetime

async def sync_local_files(folderpath: str, specific: bool = False):
    try:
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            if specific:
                with open(f"{folderpath}", "r") as file:
                    data = json.load(file)
                    print(file.name.replace(".json", "").split("/")[-1])
                    try:
                        print("Updating")
                        await db.update(f'endpoints:`{file.name.replace(".json", "").split("/")[-1]}`', data)
                    except:
                        print("Creating")
                        await db.create(f'endpoints:`{file.name.replace(".json", "").split("/")[-1]}`', data)
                    return True
            for file in os.listdir(folderpath):
                with open(f"{folderpath}/{file}", "r") as file:
                    data = json.load(file)
                    print(file.name)
                    try:
                        print("Updating")
                        await db.update(f'endpoints:`{file.name.replace(".json", "").split("/")[-1]}`', data)
                    except:
                        print("Creating")
                        await db.create(f'endpoints:`{file.name.replace(".json", "").split("/")[-1]}`', data)
            return True
    except Exception as e:
        raise errors.SurrealDBHandler.SyncLocalFilesError(e)


async def sync_server_relations():
    try:
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            for platform in ["guilded_servers", "revolt_servers", "nerimity_servers"]:
                for file in os.listdir(f"{pathlib.Path(__file__).parent.parent.resolve()}/Bot/{platform}"):
                    with open(f"{pathlib.Path(__file__).parent.parent.resolve()}/Bot/{platform}/{file}", "r") as file:
                        data = json.load(file)
                        print(file.name)
                        print(data)
                        try:
                            print("Updating")
                            _data = await db.query(f"SELECT * FROM {platform}:`{file.name.replace('.json', '').split('/')[-1]}`")
                            _data = _data[0]["result"][0]
                            await db.update(f'{platform}:`{file.name.replace(".json", "").split("/")[-1]}`', data)
                        except:
                            print("Creating")
                            await db.create(f'{platform}:`{file.name.replace(".json", "").split("/")[-1]}`', data)
            return True
    except Exception as e:
        raise errors.SurrealDBHandler.SyncLocalFilesError(e)
    


async def get_endpoint(endpoint: int, caller: str):
    try:
        print(f"{endpoint} called by {caller}")
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            data = await db.query(f"SELECT * FROM endpoints:`{endpoint}`")
            if not data:
                raise errors.SurrealDBHandler.EndpointNotFoundError(f"Endpints exists, but data was found for endpoint {endpoint}")
            data[0]["result"][0].pop("id") # Remove the id field from the data
            return data[0]["result"][0]
    except IndexError as e:
        raise errors.SurrealDBHandler.EndpointNotFoundError(e)
    except Exception as e:
        traceback.print_exc()
        raise errors.SurrealDBHandler.GetEndpointError(f"[{endpoint}] {e}")

async def create(endpoint: int, data: dict):
    try:
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            await db.query(f"CREATE endpoints:`{endpoint}` CONTENT {data}")
            return await db.query(f"SELECT * FROM endpoints:`{endpoint}`")
    except Exception as e:
        raise errors.SurrealDBHandler.CreateEndpointError(e)

async def update(endpoint: int, data: dict):
    try:
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            await db.update(f"endpoints:`{endpoint}`", data)
            return await db.query(f"SELECT * FROM endpoints:`{endpoint}`")
    except Exception as e:
        raise errors.SurrealDBHandler.UpdateEndpointError(e)

async def delete(endpoint: int):
    try:
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            await db.query(f"DELETE endpoints:`{endpoint}`")
            for platform in ["guilded_servers", "revolt_servers", "nerimity_servers"]:
                for server in await db.query(f"SELECT * FROM {platform}"):
                    if str(server["result"][0]["discord"]) == str(endpoint):
                        await db.query(f"DELETE {platform}:`{server['result'][0]['id']}`")
                        print(f"Deleted {platform}:`{server['result'][0]['id']}`")
            return True
    except Exception as e:
        raise errors.SurrealDBHandler.DeleteEndpointError(e)


async def mark_read(endpoint, platform):
    try:
        print(f"Marking {platform} read")
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            await db.query(f"UPDATE endpoints:`{endpoint}` SET meta.read.{platform} = true")
        return True
    except errors.ReadHandlerError.AlreadyReadError as e:
        return True
    except Exception as e:
        raise errors.ReadHandlerError.MarkReadError(e)


async def get_all_endpoints():
    try:
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            results = await db.query("SELECT id FROM endpoints")
            results = results[0]["result"]
            results = [result["id"] for result in results]
            results = [result.replace("endpoints:⟨", "").replace("⟩", "") for result in results]
            return results
    except Exception as e:
        raise errors.SurrealDBHandler.GetEndpointError(e)


async def write_to_structure(endpoint, key, value):
    print(f"Writing {key} to {endpoint}")
    try:
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            print(key, value)
            await db.query(f"UPDATE endpoints:`{endpoint}` SET {key} = {value}")
            return await db.query(f"SELECT * FROM endpoints:`{endpoint}`")
    except Exception as e:
        raise errors.SurrealDBHandler.UpdateEndpointError(e)


class AttachmentProcessor:

    @classmethod
    async def create_attachment(cls, attachment_id: str, status: str, type: str, registeredPlatforms: list):
        if status and status not in ["downloading", "downloaded", "sent", "canDelete"]:
            raise errors.SurrealDBHandler.CreateAttachmentError(f"Invalid status: {status}")
        if type and type not in ["jpeg", "jpg", "mp4", "png", "gif", "webp"]:
            raise errors.SurrealDBHandler.CreateAttachmentError(f"Invalid type: {type}")
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                await db.create(f"attachments:`{attachment_id}`", {"status": status, "type": type, "sentBy": {"discord": True, "guilded": True, "revolt": True, "nerimity": True}})
                for platform in registeredPlatforms:
                    if platform == "revolt":
                        await db.query(f"UPDATE attachments:`{attachment_id}` SET sentBy.revolt = true")
                        continue
                    await db.query(f"UPDATE attachments:`{attachment_id}` SET sentBy.{platform} = false")
                return await db.select(f"attachments:`{attachment_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.CreateAttachmentError(e)

    @classmethod
    async def update_attachment(cls, attachment_id: str, status: str = None, sentby: str = None):
        if status and status not in ["downloading", "downloaded", "sent", "canDelete"]:
            raise errors.SurrealDBHandler.UpdateAttachmentError(f"Invalid status: {status}")
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                if sentby:
                    await db.query(f"UPDATE attachments:`{attachment_id}` SET sentBy.{sentby} = true")
                if status:
                    await db.query(f"UPDATE attachments:`{attachment_id}` SET status = '{status}'")
                return await db.select(f"attachments:`{attachment_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.UpdateAttachmentError(e)
    
    @classmethod
    async def delete_attachment(cls, attachment_id: str):
        if attachment_id == "eligible_endpoints":
            raise errors.SurrealDBHandler.DeleteAttachmentError("Cannot delete eligible_endpoints")
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                await db.delete(f"attachments:`{attachment_id}`")
                return True
        except Exception as e:
            raise errors.SurrealDBHandler.DeleteAttachmentError(e)
    
    @classmethod
    async def get_attachment(cls, attachment_id: str):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                return await db.select(f"attachments:`{attachment_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.GetAttachmentError(e)
    
    @classmethod
    async def check_eligibility(cls, endpoint: int):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                elegible_endpoints = await db.select("attachments:eligible_endpoints")
                print(elegible_endpoints)
                if endpoint in elegible_endpoints["endpoints"]:
                    return True
                return False

        except Exception as e:
            raise errors.SurrealDBHandler.CheckEligibilityError(e)

class GetEndpoint:

    @classmethod
    async def from_guilded_id(cls, guilded_id: str):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                return await db.select(f"guilded_servers:`{guilded_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.GetEndpointError(e)
    
    @classmethod
    async def from_revolt_id(cls, revolt_id: str):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                return await db.select(f"revolt_servers:`{revolt_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.GetEndpointError(e)
    
    @classmethod
    async def from_nerimity_id(cls, nerimity_id: str):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                return await db.select(f"nerimity_servers:`{nerimity_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.GetEndpointError(e)

class CreateEndpoint:

    @classmethod
    async def for_guilded(cls, endpoint: int, guilded_id: str):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                await db.create(f"guilded_servers:`{guilded_id}`", {"discord": endpoint})
                return await db.select(f"guilded_servers:`{guilded_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.CreateEndpointError(e)
        
    @classmethod
    async def for_revolt(cls, endpoint: int, revolt_id: str):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                await db.create(f"revolt_servers:`{revolt_id}`", {"discord": endpoint})
                return await db.select(f"revolt_servers:`{revolt_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.CreateEndpointError(e)

    @classmethod
    async def for_nerimity(cls, endpoint: int, nerimity_id: str):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                await db.create(f"nerimity_servers:`{nerimity_id}`", {"discord": endpoint})
                return await db.select(f"nerimity_servers:`{nerimity_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.CreateEndpointError(e)


class Statistics:
    
    @staticmethod
    async def getall():
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                messages = await db.select("statistics:messages")
                entpoints = len(await db.select("endpoints"))

                return {
                    "messages": messages,
                    "endpoints": entpoints
                }
        except Exception as e:
            raise errors.SurrealDBHandler.GetStatisticsError(e)
    
    @staticmethod
    async def get_messages():
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                return await db.select("statistics:messages")
        except Exception as e:
            raise errors.SurrealDBHandler.GetStatisticsError(e)
    
    @staticmethod
    async def update_messages(increment: int, start_period: bool = False):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                current = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp())
                total = await db.select("statistics:messages")
                total = total["total"]
                await db.query(f"UPDATE statistics:messages SET total = {total + increment}")
                if start_period:
                    await db.query(f"UPDATE statistics:messages SET periodStart = {datetime.datetime.now().timestamp()}")
                    await db.query(f"UPDATE statistics:messages SET month = 0")
                period_start = await db.select("statistics:messages")
                period_start = period_start["periodStart"]
                print(datetime.datetime.fromtimestamp(period_start) + datetime.timedelta(weeks=4))
                if current >= datetime.datetime.fromtimestamp(period_start) + datetime.timedelta(weeks=4):
                    await db.query(f"UPDATE statistics:messages SET periodStart = {datetime.datetime.now().timestamp()}")
                    await db.query(f"UPDATE statistics:messages SET month = 0")
                else:
                    moth = await db.select("statistics:messages")
                    moth = moth["month"]
                    await db.query(f"UPDATE statistics:messages SET month = {moth + increment}")
                
                return await db.select("statistics:messages")
        except Exception as e:
            traceback.print_exc()
            raise errors.SurrealDBHandler.GetStatisticsError(e)
        

class Suspension:

    @classmethod
    async def get_suspend_status(cls, endpoint_id):
        try:
            async with Surreal(config.SDB_URL) as db:
                await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                return await db.select(f"suspensions:`{endpoint_id}`")
        except Exception as e:
            raise errors.SurrealDBHandler.GetSuspensionStatusError(e)
    

    class Endpoints:
        @classmethod
        async def suspend(cls, endpoint_id, reason, suspended_by: int, expire_at: int = None):
            data = {
                "reason": reason,
                "expireAt": expire_at,
                "type": "endpoint",
                "suspended": True,
                "suspendedAt": datetime.datetime.now().timestamp(),
                "suspendedBy": suspended_by
            }
            try:
                async with Surreal(config.SDB_URL) as db:
                    await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                    await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                    await db.create(f"suspensions:`{endpoint_id}`", data)
                    return await db.select(f"suspensions:`{endpoint_id}`")
            except Exception as e:
                raise errors.SurrealDBHandler.SuspendEndpointError(e)
        
        @classmethod
        async def unsuspend(cls, endpoint_id):
            try:
                async with Surreal(config.SDB_URL) as db:
                    await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                    await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                    await db.delete(endpoint_id)
                    print(f"Endpoint {endpoint_id} has been unsuspended")
                    return True
            except Exception as e:
                raise errors.SurrealDBHandler.UnsuspendEndpointError(e)
                    
        @classmethod
        async def update(cls, endpoint_id, reason: str = None, suspended_by: int = None, expire_at: int = None):
            data = {}
            if reason:
                data["reason"] = reason
            if suspended_by:
                data["suspendedBy"] = suspended_by
            if expire_at:
                data["expireAt"] = expire_at
  
            try:
                async with Surreal(config.SDB_URL) as db:
                    await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                    await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                    current_data = await db.select(f"suspensions:`{endpoint_id}`")
                    for key in data:
                        current_data[key] = data[key]
                    await db.update(f"suspensions:`{endpoint_id}`", current_data)
                    return await db.select(f"suspensions:`{endpoint_id}`")
            except Exception as e:
                raise errors.SurrealDBHandler.SuspendEndpointError(e)
        
        @staticmethod
        async def _checkexpireloop():
            try:
                async with Surreal(config.SDB_URL) as db:
                    await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                    await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                    data = await db.select("suspensions")
                    for suspension in data:
                        print(f"Checking {suspension['id']}")
                        if datetime.datetime.now() >= datetime.datetime.fromtimestamp(suspension["suspendedAt"]):
                            print(f"Endpoint {suspension['id']} has expired")
                            await Suspension.Endpoints.unsuspend(suspension["id"])
                    return True
            except Exception as e:
                raise errors.SurrealDBHandler.SuspensionHandlerError(e)
        
        @staticmethod   
        async def _checkendpointdatadeletionloop():
            try:
                async with Surreal(config.SDB_URL) as db:
                    await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
                    await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
                    data = await db.select("endpoints")
                    for endpoint in data:
                        print(f"Checking {endpoint['id']}")
                        if not endpoint["expireAt"] and datetime.datetime.now() <= datetime.datetime.fromtimestamp(endpoint["suspendetAt"]) + datetime.timedelta(weeks=1):
                            await delete(endpoint["id"])
                    return True
            except Exception as e:
                raise errors.SurrealDBHandler.SuspensionHandlerError(e)
            