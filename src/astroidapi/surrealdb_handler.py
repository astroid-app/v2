from surrealdb import Surreal
import os
import json
from Bot import config
import astroidapi.errors as errors

async def sync_local_files(folderpath: str):
    try:
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            for file in os.listdir(folderpath):
                with open(f"{folderpath}/{file}", "r") as file:
                    data = json.load(file)
                    print(file.name)
                    try:
                        await db.query(f'CREATE endpoints:`{file.name.replace(".json", "").split("/")[-1]}` CONTENT {data}')
                    except:
                        await db.query(f'UPDATE endpoints:`{file.name.replace(".json", "").split("/")[-1]}` CONTENT {data}')
            return True
    except Exception as e:
        raise errors.SurrealDBHandler.SyncLocalFilesError(e)

async def get_endpoint(endpoint: int):
    try:
        print(f"{endpoint} called by {__file__}")
        async with Surreal(config.SDB_URL) as db:
            await db.signin({"user": config.SDB_USER, "pass": config.SDB_PASS})
            await db.use(config.SDB_NAMESPACE, config.SDB_DATABASE)
            data = await db.query(f"SELECT * FROM endpoints:`{endpoint}`")
            try:
                data[0]["result"][0].pop("id") # Remove the id field from the data
                return data[0]["result"][0]
            except IndexError as e:
                raise errors.SurrealDBHandler.GetEndpointError.EndpointNotFoundError(e)
    except IndexError as e:
        raise errors.SurrealDBHandler.GetEndpointError.EndpointNotFoundError(e)
    except Exception as e:
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
            return True
    except Exception as e:
        raise errors.SurrealDBHandler.DeleteEndpointError(e)


