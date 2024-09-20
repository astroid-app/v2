import astroidapi.surrealdb_handler as surrealdb_handler
import asyncio
import astroidapi.errors as errors
import json


class HealthCheck:
    class EndpointCheck:

        @classmethod
        async def check(cls, endpoint):
            healthy_endpoint_data = {
                "config": {
                    "self-user": False,
                    "webhooks": {
                        "discord": [],
                        "guilded": [],
                        "revolt": [],
                        "nerimity": []
                    },
                    "channels": {
                        "discord": [],
                        "guilded": [],
                        "revolt": [],
                        "nerimity": []
                    },
                    "logs": {
                        "discord": None,
                        "guilded": None,
                        "revolt": None,
                        "nerimity": None
                    },
                    "blacklist": [],
                    "allowed-ids": [],
                    "isbeta": False
                },
                "meta": {
                    "sender-channel": None,
                    "trigger": False,
                    "sender": None,
                    "read": {
                        "discord": False,
                        "guilded": False,
                        "revolt": False,
                        "nerimity": False
                    },
                    "message": {
                        "author": {
                            "name": None,
                            "avatar": None,
                            "id": None
                        },
                        "content": None,
                        "attachments": []
                    }
                }
            }
            try:
                endpoint_data = await surrealdb_handler.get_endpoint(endpoint)
                for key in healthy_endpoint_data["config"].keys():
                    if key not in endpoint_data["config"]:
                        raise errors.HealtCheckError.EndpointCheckError.EndpointConfigError(f"'{key}' not found in endpoint config '{endpoint}'")
                for key in healthy_endpoint_data["meta"].keys():
                    if key not in endpoint_data["meta"]:
                        raise errors.HealtCheckError.EndpointCheckError.EndpointMetaDataError(f"'{key}' not found in endpoint meta data '{endpoint}'")
                print("Endpoint is healthy")
                return True
            except IndexError as e:
                raise errors.HealtCheckError.EndpointCheckError(e)


asyncio.run(HealthCheck.EndpointCheck.check(1045437427965231284))