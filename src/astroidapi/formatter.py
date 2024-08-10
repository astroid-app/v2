import re

class Format:

    @classmethod
    def format_username(cls, username: str):
        username = re.sub(r"[^\w\s]", "", username)
        username = re.sub(r"^[+\s]+|[+\s]+$", "", username)
        return username
