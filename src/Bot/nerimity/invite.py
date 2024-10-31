class Invite():
    """
    Represents a server invite in Nerimity.

    id: Snowflake ID of the invite. 
    code: Join code of invite.
    is_custom: If the invite is custom or not.
    uses: How often it was used:
    server_id: Snowflake ID of the server.
    creator_id: Snowflake ID of the user that created it.
    created_at: Timestamp from when the invite was created.
    """

    def __init__(self) -> None:
        self.id         : int   = None
        self.code       : str   = None
        self.is_custom  : bool  = None
        self.uses       : int   = None
        self.server_id  : int   = None
        self.creator_id : int   = None
        self.created_at : float = None