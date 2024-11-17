import re

class Format:

    @classmethod
    def format_username(cls, username: str):
        username = re.sub(r"[^\w\s]", "", username)
        username = re.sub(r"^[+\s]+|[+\s]+$", "", username)
        return username
    
    @classmethod
    def format_urlsafe(cls, message: str):
        message = message.replace("?", "%3F").replace("&", "%26")
    
    @classmethod
    def unformat_urlsafe(cls, message: str):
        message = message.replace("%3F", "?").replace("%26", "&")
