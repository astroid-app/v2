import re

class Format:

    @classmethod
    def format_message(cls, message: str):
        message = cls.removemarkdownlinks(message)
        return message
    
    @classmethod
    def removemarkdownlinks(cls, message: str):
        message = re.sub(r"\[(.*?)\]\((.*?)\)", r"\2", message)
        return message

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
    
    @classmethod
    def format_links_guilded_safe(cls, message: str):
        message = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", message)
        message = re.sub(r"(https?://[^\s]+)", r"[\1](\1)", message)
        return message
