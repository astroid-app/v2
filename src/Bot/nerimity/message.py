from nerimity.member import Member
from nerimity.attachment import Attachment
from nerimity._enums import GlobalClientInformation, ConsoleShortcuts

import requests
import json

class Message():
    """
    Represents a message in Nerimity.

    id: Snowflake ID of the message.
    content: Content of the message.
    type: Type of the message.
    channel_id: The ID of the channel where the message originated from.
    author_id: The ID of the author.
    edited_at: Timestamp from when the message was edited, None if not edited.
    created_at: Timestamp from when the message was created.
    embed: List of embeds.
    mentions: List of mentions.
    quoted_messages: List of quoted messages.
    reactions: List of reactions.
    attachments: List of attachments.
    author: A Member object representing the author of the message.
    
    delete(channel_id): Deletes this message. Requires ownership of the message or Administration permission in the server.
    edit(channel_id, edited_content): Edits this message to the new message content.
    react(channel_id, edited_content): Reacts to the message with the specified emoji.
    unreact(channel_id, edited_content): Unreacts the message with the specified emoji.

    deserialize(json): static | Deserialize a json string to a Message object.
    """

    def __init__(self) -> None:
        self.id              : int                      = None
        self.content         : str                      = None
        self.type            : int                      = None
        self.channel_id      : int                      = None
        self.author_id       : int                      = None
        self.edited_at       : float | None             = None
        self.created_at      : float                    = None
        self.embed           : str                      = None
        self.mentions        : list | None              = None
        self.quoted_messages : list | None              = None
        self.reactions       : list | None              = None
        self.attachments     : list[Attachment] | None  = None
        self.author          : Member                   = Member()
    
    # Public: Deletes this message. Requires ownership of the message or Administration permission in the server.
    def delete(self) -> None:
        """Deletes this message. Requires ownership of the message or Administration permission in the server."""

        api_endpoint = f"https://nerimity.com/api/channels/{self.channel_id}/messages/{self.id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.delete(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to delete {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
    
    # Public: Edits this message to the new message content.
    def edit(self, edited_content: str):
        """Edits this message to the new message content."""

        api_endpoint = f"https://nerimity.com/api/channels/{self.channel_id}/messages/{self.id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "content": edited_content,
        }

        response = requests.patch(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to edit {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
        
    # Public: Reacts to the message with the specified emoji.
    def react(self, emoji: str):
        """Reacts to the message with the specified emoji."""

        api_endpoint = f"https://nerimity.com/api/channels/{self.channel_id}/messages/{self.id}/reactions"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "name": emoji,
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to add '{emoji}' to {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Unreacts the message with the specified emoji.
    def unreact(self, emoji: str):
        """Unreacts the message with the specified emoji."""

        api_endpoint = f"https://nerimity.com/api/channels/{self.channel_id}/messages/{self.id}/reactions/remove"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "name": emoji,
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to add {emoji} to {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public Static: Deserialize a json string to a Message object.
    @staticmethod
    def deserialize(json: dict) -> 'Message':
        """static | Deserialize a json string to a Message object."""

        new_message = Message()
        new_message.id              = int(json["id"])
        new_message.content         = str(json["content"])
        new_message.type            = int(json["type"])
        new_message.channel_id      = int(json["channelId"])
        new_message.author_id       = int(json["createdById"])
        new_message.edited_at       = float(json["editedAt"])                                           if json["editedAt"]       is not None else None
        new_message.created_at      = float(json["createdAt"])
        new_message.embed           = str(json["embed"])
        new_message.mentions        = list(json["mentions"])                                            if json["mentions"]       is not None else []
        new_message.quoted_messages = list(json["quotedMessages"])                                      if json["quotedMessages"] is not None else []
        new_message.reactions       = list(json["reactions"])                                           if json["reactions"]      is not None else []
        new_message.attachments     = list(Attachment.deserialize(i) for i in json["attachments"])      if json["attachments"]    is not None else []
        new_message.author          = Member.deserialize(json["createdBy"])

        return new_message