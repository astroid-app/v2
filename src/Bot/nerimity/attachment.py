from nerimity._enums import AttachmentTypes

class Attachment():
    """
    Represents an attachment in Nerimity.

    construct(): static | Creates a new Attachment object from a file path.
    deserialize(): static | Deserialize a json string to a Attachment object.
    """

    def __init__(self) -> None:
        self.internal_type  : int               = None
        self.data_type      : str | None        = None
        self.size           : int | None        = None
        self.data           : str | None        = None
        self.height         : int | None        = None
        self.width          : int | None        = None
        self.path           : str | None        = None
        self.id             : int | None        = None
        self.provider       : str | None        = None
        self.file_id        : str | None        = None
        self.mime           : str | None        = None
        self.created_at     : float | None      = None

    # Public Static: Creates a new Attachment object from a file.
    @staticmethod
    def construct(file_path) -> 'Attachment':
        """Creates a new Attachment object from a file path."""

        new_attachment = Attachment()
        new_attachment.internal_type = AttachmentTypes.OUTGOING

        with open(file_path, 'rb') as file:
            new_attachment.data = file.read()
            new_attachment.data_type = 'application/octet-stream'
            new_attachment.size = len(new_attachment.data)
        
        return new_attachment
    
    # Public Static: Deserialize a json string to a Attachment object.
    @staticmethod
    def deserialize(json: dict) -> 'Attachment':
        """Deserialize a json string to a Attachment object."""

        new_attachment = Attachment()
        new_attachment.internal_type    = AttachmentTypes.INCOMING
        new_attachment.height           = json["height"]
        new_attachment.width            = json["width"]
        new_attachment.path             = json["path"]
        new_attachment.id               = int(json["id"])       if json["id"] is not None else None
        new_attachment.provider         = json["provider"]
        new_attachment.file_id          = json["fileId"]
        new_attachment.mime             = json["mime"]
        new_attachment.created_at       = json["createdAt"]

        return new_attachment