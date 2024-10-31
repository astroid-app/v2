import datetime

class GlobalClientInformation():
    TOKEN = ''
    SERVERS = {}

class ConsoleShortcuts():
    def log():   return f"{Colors.MAGENTA}[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}]{Colors.WHITE} |"
    def ok():    return f"{Colors.GREEN}[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}]{Colors.WHITE} |"
    def warn():  return f"{Colors.YELLOW}[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}]{Colors.WHITE} |"
    def error(): return f"{Colors.RED}[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}]{Colors.WHITE} |"

class Colors():
    BLACK = "\u001b[30m"
    RED = "\u001b[31m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BLUE = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN = "\u001b[36m"
    WHITE = "\u001b[37m"

class ChannelPermissions():
    PRIVATE_CHANNEL = 1
    SEND_MESSAGES = 2
    JOIN_VOICE = 4

class RolePermissions():
    ADMINISTRATOR = 1
    SEND_MESSAGES = 2
    MANAGE_ROLES = 4
    MANAGE_CHANNELS = 8
    KICK_USER = 16
    BAN_USER = 32
    MENTION_EVERYONE = 64

class ChannelTypes():
    DM_TEXT = 0
    SERVER_TEXT = 1
    CATEGORY = 2

class PresenceTypes():
    OFFLINE = 0
    ONLINE = 1
    LTP = 2
    AFK = 3
    DND = 4

class BadgeTypes():
    OWNER = 1
    ADMIN = 2
    CONTRIBUTOR = 4
    SUPPORTER = 8
    BOT = 16

class MessageType():
    CONTENT = 0
    JOIN_SERVER = 1
    LEAVE_SERVER = 2
    KICK_USER = 3
    BAN_USER = 4
    CALL_STARTED = 5

class AttachmentTypes():
    INCOMING = 0
    OUTGOING = 1