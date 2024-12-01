from nerimity.message import Message
from nerimity.attachment import Attachment
from nerimity._enums import GlobalClientInformation, ConsoleShortcuts

import requests
import json

class Channel():
    """
    Represents a channel in Nerimity.

    id: Snowflake ID of the channel
    name: Name of the channel.
    type: Type of the channel
    creator_id: ID of the creator of the channel.
    server_id: ID of the server the channel is in.
    category_id: ID of the category the channel is in.
    last_messaged_at: Timestamp from when the last message was send.
    created_at: Timestamp from when the channel was created.
    order: Priority of the channel in its category.
    
    update_channel(): Updates itself with specified information.
    send_message(): Sends a message to the channel.
    get_messages(): Gets a list of up to 50 message from the channel.

    deserialize(json): static | Deserialize a json string to a Channel object.
    """

    def __init__(self) -> None:
        self.id               : int             = None
        self.name             : str             = None
        self.type             : int             = None
        self.creator_id       : int             = None
        self.server_id        : int             = None
        self.category_id      : int             = None
        self.last_messaged_at : float | None    = None
        self.created_at       : float           = None
        self.order            : int | None      = None
    
    # Public: Updates itself with specified information.
    def update_channel(self, server_id: int, name: str=None, icon: str=None, content: str=None) -> None:
        """Updates itself with specified information."""

        api_endpoint = f"https://nerimity.com/api/servers/{server_id}/channels/{self.id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "name": name,
            "icon": icon,
        }

        if icon == None: del data["icon"]

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to update a channel for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
        
        if (content != None):
            api_endpoint = f"https://nerimity.com/api/servers/{server_id}/channels/{self.id}/notice"

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

    # Public: Sends a message to the channel.
    def send_message(self, message_content: str, attachments: list[Attachment] | None = None) -> None:
        """Sends a message to the channel."""

        api_endpoint = f"https://nerimity.com/api/channels/{self.id}/messages"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
        }
        data = {
            "content": message_content,
        }
        files = None

        if attachments is not None:
            for attachment in attachments:
                files = {
                    'attachment': ('Unbenannt.PNG', attachment.data),
                }

        response = requests.post(api_endpoint, headers=headers, data=data, files=files)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to send message to {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
    
    # Private: Gets a raw string of messages.
    def _get_messages_raw(self, amount: int) -> str:
        if amount > 50:
            amount = 50
        elif amount < 1:
            raise ValueError("Amount of requested messages must be positive.")

        api_endpoint = f"https://nerimity.com/api/channels/{self.id}/messages?limit={amount}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.get(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"Failed to get messages from {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
        
        return response.text

    # Public: Gets a list of up to 50 message from the channel.
    def get_messages(self, amount: int) -> list[Message]:
        """Gets a list of up to 50 message from the channel."""

        messages_raw = json.loads(self._get_messages_raw(amount))
        messages = []
        for message_raw in messages_raw:
            message = Message.deserialize(message_raw)
            messages.append(message)
        
        return messages
    
    # Public: Purge the channel of the specified amount of messages.
    def purge(self, amount: int) -> None:
        """Purges the channel of the specified amount of messages."""

        if amount > 50: print(f"{ConsoleShortcuts.warn()} Attempted to purge an illegal amount '{amount}' of mesages in {self}."); amount = 50
        if amount <= 0: print(f"{ConsoleShortcuts.warn()} Attempted to purge an illegal amount '{amount}' of mesages in {self}."); return

        messages = self.get_messages()
        messages.reverse()
        messages = messages[:amount]
        for message in messages:
            message.delete()

    # Public Static: Deserialize a json string to a Channel object.
    @staticmethod
    def deserialize(json: dict) -> 'Channel':
        """static | Deserialize a json string to a Channel object."""

        new_channel = Channel()
        new_channel.id                  = int(json["id"])
        new_channel.name                = str(json["name"])
        new_channel.type                = int(json["type"])
        new_channel.creator_id          = int(json["createdById"])      if json["createdById"]    is not None else 0
        new_channel.server_id           = int(json["serverId"])         if json["serverId"]       is not None else 0
        new_channel.category_id         = int(json["categoryId"])       if json["categoryId"]     is not None else 0
        new_channel.last_messaged_at    = float(json["lastMessagedAt"]) if json["lastMessagedAt"] is not None else None
        new_channel.created_at          = float(json["createdAt"])
        new_channel.order               = json["order"]
    
        return new_channel