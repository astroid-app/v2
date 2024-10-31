from nerimity._enums import GlobalClientInformation, ConsoleShortcuts

import requests
import json

class Post():
    """
    Represents a post in Nerimity.

    delete_post(): Deletes this post. Requires ownership over the post.
    get_comments(): Gets the comment as a list of Posts.
    like(): Likes the post.
    unlike(): Unlikes the post.

    deserialize(json): static | Deserialize a json string to a Post object.
    """

    def __init__(self) -> None:
        from nerimity.member import Member       # Lazy Import :)

        self.id             : int           = None
        self.creator_id     : int           = None
        self.content        : str           = None
        self.created_at     : float         = None
        self.edited_at      : float | None  = None
        self.quoted_post_id : int | None    = None
        self.comment_to_id  : int | None    = None
        self.deleted        : bool          = None
        self.creator        : Member        = Member()
        self.liked_by       : list[int]     = []
        self.attachments    : list          = []

    # Public: Deletes this post. Requires ownership over the post.
    def delete_post(self) -> None:
        """Deletes this post. Requires ownership over the post. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/posts/{self.id}"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.delete(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to delete {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Gets the comment as a list of Posts.
    def get_comments(self) -> list['Post']:
        """Gets the comment as a list of Post. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/posts/{self.id}/comments"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }

        response = requests.get(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to get comments for {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
    
    # Public: Likes the post.
    def like(self) -> None:
        """Likes the post. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/posts/{self.id}/like"
        self.liked_by.append({"id": self.id})

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        json.dumps(self, default=vars)

        response = requests.post(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to like {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException
    
    # Public: Unlikes the post.
    def unlike(self) -> None:
        """Unlikes the post. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/posts/{self.id}/unlike"
        self.liked_by.remove({"id": self.id})

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        json.dumps(self, default=vars)

        response = requests.post(api_endpoint, headers=headers)
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to like {self}. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public: Creates a comment to the post.
    def create_comment(self, message_content: str) -> None:
        """Creates a post and publishes it. NOT CURRENTLY POSSIBLE."""
        return

        api_endpoint = f"https://nerimity.com/api/posts"

        headers = {
            "Authorization": GlobalClientInformation.TOKEN,
            "Content-Type": "application/json",
        }
        data = {
            "content": message_content,
            "postId": f"{self.id}",
        }

        response = requests.post(api_endpoint, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            print(f"{ConsoleShortcuts.error()} Failed to create a post. Status code: {response.status_code}. Response Text: {response.text}")
            raise requests.RequestException

    # Public Static: Deserialize a json string to a Post object.
    @staticmethod
    def deserialize(json: dict) -> 'Post':
        """static | Deserialize a json string to a Message object."""
        
        from nerimity.member import Member       # Lazy Import :)
        
        new_post = Post()
        new_post.id             = int(json["id"])
        new_post.creator_id     = int(json["createdById"])
        new_post.content        = str(json["content"])
        new_post.created_at     = float(json["createdAt"])
        new_post.edited_at      = float(json["editedAt"])   if json["editedAt"]     is not None else None
        new_post.quoted_post_id = json["quotedPostId"]
        new_post.comment_to_id  = int(json["commentToId"])  if json["commentToId"]  is not None else None
        new_post.deleted        = bool(json["deleted"])     if json["deleted"]      is not None else False
        new_post.creator        = Member.deserialize(json["createdBy"])
        new_post.liked_by       = [int(i["id"]) for i in json["likedBy"]]
        new_post.attachments    = json["attachments"]

        return new_post