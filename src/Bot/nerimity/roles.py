from nerimity._enums import GlobalClientInformation, ConsoleShortcuts

import requests
import json

class Role():
    """
    Represents a role in Nerimity.

    id: Snowflake ID of the role.
    name: The name of the role.
    permissions: Integer that represents the permissions of the role.

    update_role(): Updates itself with the specified information.

    deserialize(json): static | Deserialize a json string to a Role object.
    """

    def __init__(self) -> None:
        self.id          : int          = None
        self.name        : str          = None
        self.permissions : int          = None
        self.hex_color   : str          = None
        self.creator_id  : int          = None
        self.server_id   : int          = None
        self.order       : int          = None
        self.hide_role   : bool         = None
        self.bot_role    : bool         = None
        self.created_at  : float        = None

    # Public: Updates itself with the specified information.
    def update_role(self, server_id: int, name: str=None, hex_color: str=None, hide_role: bool=None, permissions: int=None) -> None:
        """Updates itself with the specified information."""
        
        api_endpoint = f"https://nerimity.com/api/servers/{server_id}/roles/{self.id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "name": name,
            "hexColor": hex_color,
            "hideRole": hide_role,
            "permissions": permissions
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to update a role for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public Static: Deserialize a json string to a Role object.
    @staticmethod
    def deserialize(json: dict) -> 'Role':
        """static | Deserialize a json string to a Role object."""

        new_role = Role()
        new_role.id          = int(json["id"])
        new_role.name        = str(json["name"])
        new_role.permissions = int(json["permissions"])     if json["permissions"] is not None else 0
        new_role.hex_color   = str(json["hexColor"])
        new_role.creator_id  = int(json["createdById"])
        new_role.server_id   = int(json["serverId"])
        new_role.order       = int(json["order"])
        new_role.hide_role   = bool(json["hideRole"])
        new_role.bot_role    = bool(json["botRole"])        if json["botRole"]     is not None else False
        new_role.created_at  = float(json["createdAt"])

        return new_role