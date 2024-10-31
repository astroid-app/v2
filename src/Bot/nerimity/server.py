from nerimity._enums import GlobalClientInformation, ConsoleShortcuts
from nerimity.invite import Invite
from nerimity.member import Member, ServerMember
from nerimity.channel import Channel
from nerimity.roles import Role

import requests
import json

class Server():
    """
    Represents a server in Nerimity.

    id: Snowflake ID of the server.              
    name: Name of the server.
    avatar: Link to the avatar of the server.
    banner: Link to the banner of the server.
    hex_color: Hex Code of the color of the server.
    default_channel_id: ID of the default channel.
    system_channel_id: ID of the system channel.
    default_role_id: ID of the @everyone role.
    created_by_id: ID of the creator of the server.
    created_at: Timestamp from when the server was created.
    verified: Boolean on weather or not the bot is verified.
    member_count: Member count of the server.

    get_ban_list(): Returns a list of banned Members.
    get_server_details(): Updates self with information.
    create_channel(name, type): Creates a new channel for this server.
    create_invite(): Creates an invite for this server.
    create_role(): Creates a new, empty role for this server.
    delete_channel(channel_id): Deletes the specified channel from this server.
    delete_invite(): Deletes the specified invite form this server.
    delete_role(): Delete the specified channel from this server.
    update_channel(*args): Updates the specified channel with new information.
    update_member(*args): Update a member from this server.
    update_role(*args): Updates the specified role with new information.

    deserialize(json): static | Deserialize a json string to a Server object.
    """

    def __init__(self) -> None:
        self.id                 : int           = None
        self.name               : str           = None
        self.avatar             : str           = None
        self.banner             : str           = None
        self.hex_color          : str           = None
        self.default_channel_id : int           = None
        self.system_channel_id  : int | None    = None
        self.default_role_id    : int           = None
        self.created_by_id      : int           = None
        self.created_at         : float         = None
        self.verified           : bool          = None
        self.member_count       : int           = None

        self.channels           : dict[str, Channel] = {}
        self.members            : dict[str, ServerMember]  = {}
        self.roles              : dict[str, Role] = {}

    ### Server
    # Public: Returns a list of banned Members.
    def get_ban_list(self) -> list[Member]:
        """Returns a list of banned Members."""

        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/bans/"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.get(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to get ban list {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

        list_raw = json.loads(response.text)

        if len(list_raw[0]) == 1: return []

        users = []
        for i in list_raw[0].keys():
            if i == "serverId": continue

            user_raw = list_raw[0][i]
            user = Member.deserialize(user_raw)
            users.append(user)
        
        return users

    # Public: Updates self with information.
    def get_server_details(self) -> None:
        """Updates self with information."""

        invite_code = self.create_invite()
        api_endpoint = f"https://nerimity.com/api/servers/invites/{invite_code.code}"
        
        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.get(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to get ban list {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

        server_raw = json.loads(response.content)
        self.id                 = server_raw["id"]
        self.name               = server_raw["name"]
        self.avatar             = server_raw["avatar"]
        self.banner             = server_raw["banner"]
        self.hex_color          = server_raw["hexColor"]
        self.default_channel_id = server_raw["defaultChannelId"]
        self.system_channel_id  = server_raw["systemChannelId"]
        self.default_role_id    = server_raw["defaultRoleId"]
        self.created_by_id      = server_raw["defaultRoleId"]
        self.created_at         = server_raw["createdAt"]
        self.verified           = server_raw["verified"]
        self.member_count       = server_raw["memberCount"]


    ### Members 
    # Public: Update a member from this server.
    def update_member(self, user_id: int, role_ids: list[int]=None) -> None:
        """Update a member from this server."""

        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/members/{user_id}/"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        if role_ids is not None: [str(id) for id in role_ids]
        else: role_ids = None

        data = {
            "roleIds": role_ids
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to update a member for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException


    ### Roles
    # Public: Creates a new, empty role for this server.
    def create_role(self) -> None:
        """Creates a new, empty role for this server."""
        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/roles"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.post(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to create a role for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Deletes the specified role from this server.
    def delete_role(self, role_id: int) -> None:
        """Deletes the specified role from this server."""

        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/roles/{role_id}/"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.delete(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to delete a role for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Updates the specified role with new information.
    def update_role(self, role_id: int, name: str=None, hex_color: str=None, hide_role: bool=None, permissions: int=None) -> None:
        """Updates the specified role with new information."""

        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/roles/{role_id}"

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


    ### Channels
    # Public: Creates a new channel for this server.
    def create_channel(self, name: str, type: int) -> None:
        """Creates a new channel for this server."""
    
        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/channels"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "name": name,
            "type": type,
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to create a channel for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Delete the specified channel from this server.
    def delete_channel(self, channel_id: int) -> None:
        """Delete the specified channel from this server."""

        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/channels/{channel_id}/"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.delete(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to delete a channel from {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Updates the specified channel with new information.
    def update_channel(self, channel_id: int, permissions: int=None, name: str=None, icon: str=None, content: str=None) -> None:
        """Updates the specified channel with new information."""

        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/channels/{channel_id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "permissions": permissions,
            "name": name,
            "icon": icon,
        }

        if icon == None: del data["icon"]

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to update a channel for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
        
        if (content != None):
            api_endpoint = f"https://nerimity.com/api/servers/{self.id}/channels/{channel_id}/notice"

            if content == "":
                response = requests.delete(api_endpoint, headers=headers)

                if response.status_code != 200:
                    print(f"{ConsoleShortcuts.error()} Failed to update a channel for {self}. Status code: {response.status_code}. Response Text: {response.text}")
                    raise requests.RequestException
            else:
                response = requests.put(api_endpoint, headers=headers, data=json.dumps({"content": content}))

                if response.status_code != 200:
                    print(f"{ConsoleShortcuts.error()} Failed to update a channel for {self}. Status code: {response.status_code}. Response Text: {response.text}")
                    raise requests.RequestException


    ### Invites
    # Public: Creates an invite for this server.
    def create_invite(self) -> Invite:
        """Creates an invite for this server and returns it. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/invites"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.post(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to create an invite for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException(response.status_code)
        
        invite_raw = json.loads(response.content)
        new_invite = Invite()
        new_invite.id           = int(invite_raw["id"])
        new_invite.code         = invite_raw["code"]
        new_invite.is_custom    = invite_raw["isCustom"]
        new_invite.uses         = invite_raw["uses"]
        new_invite.server_id    = invite_raw["serverId"]
        new_invite.creator_id   = invite_raw["createdById"]
        new_invite.created_at   = invite_raw["createdAt"]

        return new_invite

    # Public: Deletes the specified invite form this server.
    def delete_invite(self, code: str) -> None:
        """Deletes the specified invite form this server. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/servers/{self.id}/invites/{code}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.delete(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to delete an invite form {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException(response.status_code)
    
    
    ### Deserialize
    # Public Static: Deserialize a json string to a Server object.
    @staticmethod
    def deserialize(json: dict) -> 'Server':
        """static | Deserialize a json string to a Server object."""

        new_server = Server()
        new_server.id                 = int(json["id"])
        new_server.name               = str(json["name"])
        new_server.avatar             = str(json["avatar"])
        new_server.banner             = str(json["banner"])
        new_server.hex_color          = str(json["hexColor"])
        new_server.default_channel_id = int(json["defaultChannelId"])
        new_server.system_channel_id  = int(json["systemChannelId"])    if json["systemChannelId"] is not None else None
        new_server.default_role_id    = int(json["defaultRoleId"])
        new_server.created_by_id      = int(json["createdById"])
        new_server.created_at         = float(json["createdAt"])
        new_server.verified           = bool(json["verified"])
        new_server.member_count       = None    # why is this not send over, ugh

        new_server.channels           = {}
        new_server.members            = {}
    
        return new_server