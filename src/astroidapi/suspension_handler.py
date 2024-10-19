import astroidapi.surrealdb_handler as surrealdb_handler
import astroidapi.errors as errors
import asyncio
import threading


class Endpoint():
    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id
    
    stop_event = asyncio.Event()
    
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
    

    @classmethod
    async def check_expirations(cls):
        while not cls.stop_event.is_set():
            print("[Suspension handler] Checking expirations...")
            await surrealdb_handler.Suspension.Endpoints._checkexpireloop() 
            await asyncio.sleep(60 * 10) # 10 minutes

        print("Stopping expiration checks...")

    @classmethod
    def stop_check_expirations(cls):
        cls.stop_event.set()


def run_async_in_thread(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(coro)
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


thread = threading.Thread(target=run_async_in_thread, args=(Endpoint.check_expirations()))
thread.start()