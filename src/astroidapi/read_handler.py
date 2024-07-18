from astroidapi import errors, surrealdb_handler
import asyncio
class ReadHandler:

    @classmethod
    async def mark_read(cls, endpoint, platform):
        try:
            endpoint_data = await surrealdb_handler.get_endpoint(endpoint)
            if endpoint_data is None:
                raise errors.SurrealDBHandler.GetEndpointError.EndpointNotFoundError(f"'{endpoint}' not found")
            if await cls.check_read(endpoint, platform):
                raise errors.ReadHandlerError.AlreadyReadError(f"'{endpoint}' already marked '{platform}' as read")
            endpoint_data["meta"]["read"][platform] = True
            asyncio.create_task(surrealdb_handler.update(endpoint, endpoint_data))
            return True
        except errors.ReadHandlerError.AlreadyReadError as e:
            return True
        except Exception as e:
            raise errors.ReadHandlerError.MarkReadError(e)
    
    @classmethod
    async def check_read(cls, endpoint, platform = "all", data: dict = None):
        try:
            if data:
                print("Data provided")
                read = data["meta"]["read"]
                if platform != "all":
                    possible_platforms = ["discord", "guilded", "revolt", "nerimity"]
                    if platform not in possible_platforms:
                        raise errors.ReadHandlerError.InvalidPlatformError(f"Invalid platform '{platform}'")
                    read = read[platform]
                return read
            endpoint = await surrealdb_handler.get_endpoint(endpoint)
            if endpoint is None:
                raise errors.SurrealDBHandler.GetEndpointError.EndpointNotFoundError(f"'{endpoint}' not found")
            read = endpoint["meta"]["read"]
            if platform != "all":
                possible_platforms = ["discord", "guilded", "revolt", "nerimity"]
                if platform not in possible_platforms:
                    raise errors.ReadHandlerError.InvalidPlatformError(f"Invalid platform '{platform}'")
                read = read[platform]
            return read
        except Exception as e:
            raise errors.ReadHandlerError.MarkReadError(e)