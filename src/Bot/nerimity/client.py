from nerimity.message import Message
from nerimity._enums import GlobalClientInformation, ConsoleShortcuts, RolePermissions
from nerimity.context import Context
from nerimity.channel import Channel
from nerimity.member import Member, ServerMember, ClientMember
from nerimity.server import Server
from nerimity.roles import Role
from nerimity.post import Post

import websockets
import asyncio
import json
import requests
import time
import re

def camel_to_snake(camel_case):
    snake_case = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', camel_case)
    return snake_case.lower()

class Client:
    """
    Represents the client of the bot in Nerimity. DO NOT MODIFY THIS!

    token: The Token of the bot.
    prefix: The command prefix of the bot.
    commands: A dictionary of commands and the functions to execute said command.
    event_listeners: A dictionary of listeners events that get executed when the listener fires.
    account: A ClientMember that represents the bot account.
    servers: A dictionary of servers that the bot is in.
    pending_friends: A dict of pending friends.

    run(): Starts the bot. Any code below the start will not be executed until the bot crashes.

    @command(): decorator | Used to register a prefixed command.
    @listen(): decorator | Used to register to an event listener.
    """

    def __init__(self, token: str, prefix: str) -> None:
        self.token    : str            = token
        self.prefix   : str            = prefix
        self.commands : list[function] = {}
        self.event_listeners = {
            "on_ready": [],
            "on_message_updated": [],
            "on_message_create": [],
            "on_message_deleted": [],
            "on_presence_change": [],
            "on_reaction_add": [],
            "on_member_updated": [],
            "on_role_updated": [],
            "on_role_deleted": [],
            "on_role_created": [],
            "on_channel_updated": [],
            "on_channel_deleted": [],
            "on_channel_created": [],
            "on_server_updated": [],
            "on_member_join": [],
            "on_member_left": [],
            "on_server_joined": [],
            "on_server_left": [],
            "on_friend_request_sent": [],
            "on_friend_request_pending": [],
            "on_friend_request_accepted": [],
            "on_friend_removed": [],
            "on_minute_pulse": [],
            "on_hour_pulse": [],
        }
        self.account: ClientMember              = ClientMember()
        self.servers: dict[str, Server]         = {}
        self.pending_friends: dict[str, Member] = {}

        GlobalClientInformation.TOKEN = token

    # Public: Decorator to register a prefixed command.
    def command(self, name: str = None, aliases: list[str] = None, permissions: int = RolePermissions.SEND_MESSAGES) -> None:
        """Decorator to register a prefixed command."""

        def decorator(func):
            command_name = name if name is not None else func.__name__
            self.commands[command_name] = func

            func.permissions = permissions

            if aliases is not None:
                if not isinstance(aliases, list):
                    raise TypeError("Aliases should be a list of strings.")
                for alias in aliases:
                    self.commands[alias] = func

            return func
        return decorator

    # Public: Decorator to register to an event listener.
    def listen(self, event: str) -> None:
        """
        Decorator to register to an event listener. Unless noted otherwise a 'dict' with relevent is passed.

        Events:
        - on_ready: Triggered when the bot is ready, passes.
        - on_message_updated: Triggered when the bot sees a message being updated.
        - on_message_create: Triggered when the bot sees a message being created.
        - on_message_deleted: Triggered when the bot sees a message being delete.
        - on_presence_change: Triggered when the bot sees a user change presence.
        - on_reaction_add: Triggered when the bot sees a message get a reaction.
        - on_member_updated: Triggered when the bot sees a member getting a role in a server.
        - on_role_updated: Triggered when the bot sees a role being updated in a server.
        - on_role_deleted: Triggered when the bot sees a role being deleted in a server.
        - on_role_created: Triggered when the bot sees a role being created in a server.
        - on_channel_updated: Triggered when the bot sees a channel being updated in a server.
        - on_channel_deleted: Triggered when the bot sees a channel being deleted in a server.
        - on_channel_created: Triggered when the bot sees a channel being created in a server.
        - on_server_updated: Triggered when the bot sees a server being updated.
        - on_member_join: Triggered when the bot sees a member join a server.
        - on_member_left: Triggered when the bot sees a member leave a server.
        - on_server_joined: Triggered when the bot gets add to a server.
        - on_server_left: Triggered when the bot gets removed from a server.
        - on_friend_request_sent: *Unkown*
        - on_friend_request_pending: Triggered when there is a pending friend request to the bot.
        - on_friend_request_accepted: Triggered when a friend request is accepted. 
        - on_friend_removed: Triggered when someone removes the bot as a friend and vice versa.
        - on_minute_pulse: Triggered each minute. Does not pass anything.
        - on_hour_pulse: Triggered each hour. Does not pass anything.
        """
        if event not in self.event_listeners.keys():
            print((f"{ConsoleShortcuts.error()} Invalid event type: {event}. Use an existing event or see the documentation."))
            raise ValueError(event)
        
        def decorator(func):
            self.event_listeners[event].append(func)
            return func
        return decorator

    # Private: Triggered at the start of each minute.
    async def _minute_pulse(self) -> None:
        while True:
            await asyncio.sleep(60)

            for listener in self.event_listeners['on_minute_pulse']:    # on_minute_pulse
                await asyncio.create_task(listener.__call__())
    
    # Private: Triggered at the start of each hour.
    async def _hour_pulse(self) -> None:
        while True:
            await asyncio.sleep(3600)

            for listener in self.event_listeners['on_hour_pulse']:      # on_hour_pulse
                await asyncio.create_task(listener.__call__())
    
    # Private: Processes Commands and execute them if they exist.
    async def _process_commands(self, message: Message) -> None:
        if not message.content.startswith(self.prefix):
            return

        command = message.content.removeprefix(self.prefix).split(' ')[0]
        if command in self.commands:
            ctx = Context(message)

            if ctx.author.has_permission(self.commands[command].permissions) == False:
                print(f"{ConsoleShortcuts.ok()} {ctx.author.username}#{ctx.author.tag} attempted to run a command that required permissions they did not have.")
                ctx.respond("You do not have the required permissions to execute this command.")
                return

            arguments = message.content.split(' ')[1:]
            parsed_arguments = []
            i = 0
            while i < len(arguments):
                if arguments[i].startswith('"'):
                    combined_arg = arguments[i][1:]  # Remove the leading double quote
                    i += 1
                    while i < len(arguments) and not arguments[i].endswith('"'):
                        combined_arg += ' ' + arguments[i]
                        i += 1
                    if i < len(arguments):
                        combined_arg += ' ' + arguments[i][:-1]  # Remove the trailing double quote
                    parsed_arguments.append(combined_arg)
                else:
                    parsed_arguments.append(arguments[i])
                i += 1
        
            asyncio.create_task(self.commands[command].__call__(ctx, parsed_arguments))

    # Private: Listens to the webhook and calls commands/listeners.
    async def _listen_webhook(self, websocket: 'websockets.legacy.client.WebSocketClientProtocol') -> None:
        print(f"{ConsoleShortcuts.log()} The bot is now listening to incoming connections.")
        while True:
            message_raw: str = await websocket.recv()

            # Ping-Pong
            if message_raw == "2":
                await websocket.send("3")

            elif message_raw.startswith("42[\"message:updated"):
                    
                    for listener in self.event_listeners["on_message_updated"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"message:created"):
                    
                    message = Message.deserialize(json.loads(message_raw.removeprefix("42"))[1]["message"])
                    await self._process_commands(message)
                    
                    for listener in self.event_listeners["on_message_create"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"message:deleted"):
                    
                    for listener in self.event_listeners["on_message_deleted"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"message:reaction_added"):
                    
                    for listener in self.event_listeners["on_reaction_add"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"user:presence_update"):
                    
                    for listener in self.event_listeners["on_presence_change"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"user:server_settings_update"):
                    
                    for listener in self.event_listeners["on_server_updated"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:role_updated"):

                    message = json.loads(message_raw.removeprefix("42"))[1]
                    role = self.servers[message["serverId"]].roles[message["roleId"]]
                    for entry in message["updated"]:
                        setattr(role, camel_to_snake(entry), message["updated"][entry])
                    
                    for listener in self.event_listeners["on_role_updated"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:role_created"):

                    message = json.loads(message_raw.removeprefix("42"))[1]
                    self.servers[message["serverId"]].roles[message["id"]] = Role.deserialize(message)

                    for listener in self.event_listeners["on_role_created"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:role_deleted"):

                    message = json.loads(message_raw.removeprefix("42"))[1]
                    del self.servers[message["serverId"]].roles[message["roleId"]]
                    
                    for listener in self.event_listeners["on_role_deleted"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:member_updated"):

                    message = json.loads(message_raw.removeprefix("42"))[1]
                    member = self.servers[message["serverId"]].members[message["userId"]]
                    for entry in message["updated"]:
                        setattr(member, camel_to_snake(entry), message["updated"][entry])
                    
                    for listener in self.event_listeners["on_member_updated"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:member_joined"):
                    
                    message = json.loads(message_raw.removeprefix("42"))[1]
                    if message["serverId"] in self.servers.keys():
                        self.servers[message["serverId"]].members[message["member"]["userId"]] = ServerMember.deserialize(message["member"])
                    
                    for listener in self.event_listeners["on_member_join"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:member_left"):
                    
                    message = json.loads(message_raw.removeprefix("42"))[1]
                    del self.servers[message["serverId"]].members[message["userId"]]
                    
                    for listener in self.event_listeners["on_member_left"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:channel_updated"):
                    
                    message = json.loads(message_raw.removeprefix("42"))[1]
                    channel = self.servers[message["serverId"]].channels[message["channelId"]]
                    for entry in message["updated"]:
                        setattr(channel, camel_to_snake(entry), message["updated"][entry])
                    
                    for listener in self.event_listeners["on_channel_updated"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:channel_created"):
                    
                    message = json.loads(message_raw.removeprefix("42"))[1]
                    self.servers[message["serverId"]].channels[message["channel"]["id"]] = Channel.deserialize(message["channel"])
                    
                    for listener in self.event_listeners["on_channel_created"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:channel_deleted"):
                    
                    message = json.loads(message_raw.removeprefix("42"))[1]
                    del self.servers[message["serverId"]].channels[message["channelId"]]
                    
                    for listener in self.event_listeners["on_channel_deleted"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:joined"):

                    message = json.loads(message_raw.removeprefix("42"))[1]
                    new_server = Server.deserialize(message["server"])
                    self.servers[message["server"]["id"]] = new_server

                    for member_raw in message["members"]:
                        member = ServerMember.deserialize(member_raw)
                        self.servers[f"{member.server_id}"].members[f"{member.id}"] = member
                    for channel_raw in message["channels"]:
                        channel = Channel.deserialize(channel_raw)
                        self.servers[f"{channel.server_id}"].channels[f"{channel.id}"] = channel
                    for role_raw in message["roles"]:
                        role = Role.deserialize(role_raw)
                        self.servers[f"{role.server_id}"].roles[f"{role.id}"] = role
                    
                    for listener in self.event_listeners["on_server_joined"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"server:left"):

                    message = json.loads(message_raw.removeprefix("42"))[1]
                    del self.servers[message["serverId"]]

                    for listener in self.event_listeners["on_server_left"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"friend:request_sent"):

                    message = json.loads(message_raw.removeprefix("42"))[1]

                    for listener in self.event_listeners["on_friend_request_sent"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"friend:request_pending"):

                    message = json.loads(message_raw.removeprefix("42"))[1]
                    self.pending_friends[f"{message['recipientId']}"] = Member.deserialize(message["recipient"])

                    for listener in self.event_listeners["on_friend_request_pending"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"friend:request_accepted"):

                    try:
                        message = json.loads(message_raw.removeprefix("42"))[1]
                        self.account.friends[f"{message['friendId']}"] = self.pending_friends[f"{message['friendId']}"]
                        del self.pending_friends[f"{message['friendId']}"]
                    except KeyError:
                        print(f"{ConsoleShortcuts.error()} There was an error while trying to accept a friend request from {message['friendId']}. This likely happened due to a bot restart. It is advisable to accept/deny friend request as they come in, not afterwards as a friend object cannot be loaded if it does not have a Member object in memory.")

                    for listener in self.event_listeners["on_friend_request_accepted"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"friend:removed"):

                    message = json.loads(message_raw.removeprefix("42"))[1]
                    del self.account.friends[f"{message['friendId']}"]

                    for listener in self.event_listeners["on_friend_removed"]:
                        await asyncio.create_task(listener.__call__(json.loads(message_raw.removeprefix("42"))[1]))
            elif message_raw.startswith("42[\"channel:typing"):
                    pass
            elif message_raw.startswith("42[\"notification:dismissed"):
                    pass
            elif message_raw.startswith("0{\"sid"):
                await websocket.send("40")

                message: str = await websocket.recv()
                await websocket.send(f"42[\"user:authenticate\",{{\"token\":\"{GlobalClientInformation.TOKEN}\"}}]")

                message: str = await websocket.recv()
                del message
            else:
                print(f"{ConsoleShortcuts.warn()} Unknown event occurred with content:{message_raw}")
            
            GlobalClientInformation.SERVERS = self.servers

    # Public: Starts the bot. Any code below the start will not be executed.
    def run(self, debug_mode: bool=False) -> None:
        """Starts the bot. Any code below the start will not be executed."""
    
        async def main():
            first_start = True

            # Loop this indefinetly
            while True:
                try:
                    async with websockets.connect("wss://nerimity.com/socket.io/?EIO=4&transport=websocket") as websocket:

                        # We only want to get the data the first time so we dont overwrite on restart
                        if first_start:
                            first_start = False
                            print(f"{ConsoleShortcuts.log()} Connecting to Nerimity and starting authentication process.")

                            message: str = await websocket.recv()
                            await websocket.send("40")

                            message: str = await websocket.recv()
                            await websocket.send(f"42[\"user:authenticate\",{{\"token\":\"{GlobalClientInformation.TOKEN}\"}}]")

                            message: str = await websocket.recv()
                            print(f"{ConsoleShortcuts.log()} Authentication process finished successfully!")

                            # Load everything they send over to the servers dict
                            message_auth = json.loads(message.removeprefix("42"))[1]
                            self.account = ClientMember.deserialize(message_auth["user"])

                            for server_raw in message_auth["servers"]:
                                server = Server.deserialize(server_raw)
                                self.servers[f"{server.id}"] = server
                            self.servers["0"] = Server()

                            for member_raw in message_auth["serverMembers"]:
                                member = ServerMember.deserialize(member_raw)
                                self.servers[f"{member.server_id}"].members[f"{member.id}"] = member
                            for channel_raw in message_auth["channels"]:
                                channel = Channel.deserialize(channel_raw)
                                self.servers[f"{channel.server_id}"].channels[f"{channel.id}"] = channel
                            for role_raw in message_auth["serverRoles"]:
                                role = Role.deserialize(role_raw)
                                self.servers[f"{role.server_id}"].roles[f"{role.id}"] = role
                            for friend_raw in message_auth["friends"]:
                                friend = Member.deserialize(friend_raw["recipient"])
                                self.account.friends[f"{friend.id}"] = friend

                            GlobalClientInformation.SERVERS = self.servers

                            # on_ready
                            for listener in self.event_listeners["on_ready"]:
                                await asyncio.create_task(listener.__call__(message_auth))

                            # on_hour_pulse & on_minute_pulse
                            if self.event_listeners["on_minute_pulse"] != {}: asyncio.create_task(self._minute_pulse())
                            if self.event_listeners["on_hour_pulse"]   != {}: asyncio.create_task(self._hour_pulse())
                        await self._listen_webhook(websocket)
                except Exception as e:

                    # For some reason we cant import the actual class so we need to look at the __repr__() method instead
                    if e.__repr__().startswith('ConnectionClosed'):
                        print(f"{ConsoleShortcuts.warn()} Lost connection, attempting to reconnect.")
                    else:
                        raise e

        # Create and run an event loop
        if not debug_mode:
            last_crash = 0
            while True:
                try:
                    asyncio.get_event_loop().run_until_complete(main())
                except Exception as e:
                    print(f"{ConsoleShortcuts.error()} Bot crashed with error: {e}")
                
                if time.time() - last_crash < 60:
                    print(f"{ConsoleShortcuts.error()} Last crash happened less than a minute ago. Shutting down.")
                    exit()
                
                last_crash = time.time()
        else:
            print(f"{ConsoleShortcuts.log()} Launching in debug mode, any uncaught exception will crash the bot.")
            asyncio.get_event_loop().run_until_complete(main())