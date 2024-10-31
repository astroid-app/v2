from nerimity.attachment import Attachment
from nerimity.channel import Channel
from nerimity.member import ServerMember
from nerimity.message import Message
from nerimity.server import Server
from nerimity._enums import GlobalClientInformation

class Context():
    """
    Represents the context for the command.

    message: The message that triggered the command.
    author: The author of the message that triggered the command.
    channel: The channel where the command was triggered in.
    server: The server where the command was tirggered in

    respond(): Responds to the original message.
    remove(): Removes the original message.
    react(): Adds an emoji the original message.
    """

    def __init__(self, message: Message) -> None:
        self.message: Message       = message
        self.author : ServerMember  = None
        self.channel: Channel       = None
        self.server : Server        = None

        for server in GlobalClientInformation.SERVERS.values():
            if str(message.channel_id) in server.channels.keys():
                self.server  = GlobalClientInformation.SERVERS[f"{server.id}"]
                self.channel = GlobalClientInformation.SERVERS[f"{server.id}"].channels[f"{message.channel_id}"]
                self.author  = GlobalClientInformation.SERVERS[f"{server.id}"].members[f"{message.author_id}"]

    # Public: Responds to the original message.
    def respond(self, response: str, attachments: list[Attachment] | None = None) -> None:
        """Responds to the original message."""

        self.channel.send_message(response, attachments)

    # Public: Removes the original message.
    def remove(self) -> None:
        """Removes the original message."""

        self.message.delete()
    
    # Public: Adds an emoji the original message.
    def react(self, emoji: str) -> None:
        """Adds an emoji the original message."""

        self.message.react(emoji)