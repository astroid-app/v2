import astroidapi.surrealdb_handler as surrealdb_handler
import astroidapi.errors as errors


class Endpoint():
    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id
    
    @classmethod
    async def is_suspended(cls, endpoint_id):
        try:
            suspended = await surrealdb_handler.Suspension.get_suspend_status(endpoint_id)
            print(suspended)
        except errors.SurrealDBHandler.GetSuspensionStatusError as e:
            raise errors.SuspensionHandlerError.GetSuspensionStatusError(e)
        try:
            return suspended["suspended"]
        except KeyError:
            return False
        except TypeError:
            return False
    
    @classmethod
    async def suspend(cls, endpoint_id, reason, suspended_by: int, expire_at: int = None):
        try:
            await surrealdb_handler.Suspension.Endpoints.suspend(endpoint_id, reason, suspended_by, expire_at)
        except errors.SurrealDBHandler.SuspendEndpointError as e:
            raise errors.SuspensionHandlerError.SuspendEndpointError(e)

    @classmethod
    async def unsuspend(cls, endpoint_id):
        try:
            await surrealdb_handler.Suspension.Endpoints.unsuspend(endpoint_id)
        except errors.SurrealDBHandler.UnsuspendEndpointError as e:
            raise errors.SuspensionHandlerError.UnsuspendEndpointError(e)