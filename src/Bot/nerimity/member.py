from nerimity._enums import GlobalClientInformation, ConsoleShortcuts
from nerimity.roles import Role
from nerimity.attachment import Attachment
from nerimity.post import Post

import requests
import json

# Generic Member
class Member():
    """
    Represents a member in Nerimity.

    id: Snowflake ID of the message.
    username: The username of the member.
    tag: The tag of the member.
    hex_color: Hex color of the member's username text.
    avatar: Link to the avatar.
    badges: Numerical value of the badges the member has.

    send_message(message_content): Sends a message to the channel.
    follow(): Follows the User.
    unfollow(): Unfollows the User.
    add_friend(): Sends a friend request to the specified user.
    remove_friend(): Removes the specified user from friends.

    deserialize(json): static | Deserialize a json string to a Member object.
    """

    def __init__(self) -> None:
        self.id        : int        = None
        self.username  : str        = None
        self.tag       : str        = None
        self.hex_color : str        = None
        self.avatar    : str | None = None
        self.badges    : int        = None

    # Public: Follows the user.
    def follow(self) -> None:
        """Follows the Member. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/users/{self.id}/follow"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.post(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to follow {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Unfollows the user.
    def unfollow(self) -> None:
        """Unfollows the user. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/users/{self.id}/follow"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.delete(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to follow {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
    
    # Public: Sends a friend request to the specified user.
    def add_friend(self) -> None:
        """Sends a friend request to the specified user. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/friends/{self.id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.post(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to send a friend request to {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Removes the specified user from friends.
    def remove_friend(self) -> None:
        """Removes the specified user from friends. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/friends/{self.id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.post(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to send a friend request to {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
    
    # Public: Sends a direct message to the member.
    def send_message(self, message_content: str) -> None:
        """Sends a direct message to the member. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/channels/{self.id}/messages"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "content": message_content,
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to send message to {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public Static: Deserialize a json string to a Member object.
    @staticmethod
    def deserialize(json: dict) -> 'Member':
        """static | Deserialize a json string to a Member object."""

        new_member = Member()
        new_member.id               = int(json["id"])
        new_member.username         = str(json["username"])
        new_member.tag              = str(json["tag"])
        new_member.hex_color        = str(json["hexColor"])
        new_member.avatar           = str(json["avatar"])
        new_member.badges           = int(json["badges"])
    
        return new_member

# Member but in a server
class ServerMember(Member):
    """
    Represents a member of a server in Nerimity.
    Extension of Member.

    server_id: The server ID that the member is a part of.
    joined_at: When the user joined the server.
    role_ids: A list of IDs of the roles the user has.

    kick(): Kicks the user from the server.
    ban(soft_ban): Bans the user from the server, a softban does not remove all messages send in the last 7 hours.
    unban(): Unbans the user from the server.

    deserialize(json): static | overwrite | Deserialize a json string to a ServerMember object.
    """

    def __init__(self) -> None:
        super().__init__()
        self.server_id : int        = None
        self.joined_at : float      = None
        self.role_ids  : list[int]  = None

    def kick(self) -> None:
        """Kicks the user from the server."""

        api_endpoint = f"https://nerimity.com/api/servers/{self.server_id}/members/{self.id}/kick"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.delete(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to kick {self} from {self.server_id}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
        
    # Public: Bans the user from the server, a softban does not remove all messages send in the last 7 hours.
    def ban(self, soft_ban: bool=False) -> None:
        """Bans the user from the server, a softban does not remove all messages send in the last 7 hours."""

        if soft_ban == True:  
            api_endpoint = f"https://nerimity.com/api/servers/{self.server_id}/bans/{self.id}?shouldDeleteRecentMessages=false"
        else:
            api_endpoint = f"https://nerimity.com/api/servers/{self.server_id}/bans/{self.id}?shouldDeleteRecentMessages=true"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.post(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to ban {self} from {self.server_id}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Unbans the user from the server.
    def unban(self) -> None:
        """Unbans the user from the server."""

        api_endpoint = f"https://nerimity.com/api/servers/{self.server_id}/bans/{self.id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.delete(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to ban {self} from {self.server_id}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public Static Overwrite: Deserialize a json string to a Member object.
    @staticmethod
    def deserialize(json: dict) -> 'ServerMember':
        """static | overwrite | Deserialize a json string to a ServerMember object."""

        new_member = ServerMember()
        new_member.id               = int(json["user"]["id"])
        new_member.username         = str(json["user"]["username"])
        new_member.tag              = str(json["user"]["tag"])
        new_member.hex_color        = str(json["user"]["hexColor"])
        new_member.avatar           = str(json["user"]["avatar"])
        new_member.badges           = str(json["user"]["badges"])
        new_member.server_id        = int(json["serverId"])
        new_member.joined_at        = float(json["joinedAt"])
        new_member.role_ids         = list(json["roleIds"])

        return new_member

# Member but it is the bot
class ClientMember(Member):
    """
    Represents a member that is the bot account specifically.
    Extension of Member.

    friends: A dict containing every member with their ID as the key.

    set_presence(value, custom_text): Sets the presence of the bot.
    create_post(message_content): Creates a post and publishes it.
    get_feed(): Returns the entire feed the bot currently has.

    deserialize(json): static | overwrite | Deserialize a json string to a ClientMember object.
    """

    def __init__(self) -> None:
        super().__init__()
        self.friends: dict[str, Member] = {}

    # Public: Sets the presence of the bot.
    def set_presence(self, value: int, custom_text: str) -> None:
        """Sets the presence of the bot. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/users/presence"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "status": value,
            "custom": custom_text
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"Failed to set presence. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
        
        return response.text

    # Public: Creates a post and publishes it.
    def create_post(self, message_content: str) -> None:
        """Creates a post and publishes it. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/posts"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
        }
        data = {
            "content": message_content,
        }

        response = requests.post(api_endpoint, headers=headers, data=data)
        pass
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to send message to {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Returns the entire feed the bot currently has.
    async def get_feed(self) -> list[Post]:
        """Returns the entire feed the bot currently has. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/posts/feed"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.get(api_endpoint, headers=headers)
        raw_feed = json.loads(response.content)

        feed = []
        for raw_post in raw_feed:
            post = Post.deserialize(raw_post)
            feed.append(post)
        
        return feed

    # Public Static Overwrite: Deserialize a json string to a ClientMember object.
    @staticmethod
    def deserialize(json: dict) -> 'ClientMember':
        """static | overwrite | Deserialize a json string to a ClientMember object."""

        new_member = ClientMember()
        new_member.id               = int(json["id"])
        new_member.username         = str(json["username"])
        new_member.tag              = str(json["tag"])
        new_member.hex_color        = str(json["hexColor"])
        new_member.avatar           = str(json["avatar"])       if "avatar" in json.keys() else None
        new_member.badges           = int(json["badges"])
        new_member.friends          = {}
    
        return new_member