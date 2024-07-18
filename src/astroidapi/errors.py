


class SendingError(Exception):
    def __init__(self):
        pass

    class ChannelNotFound(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class SendFromNerimiryError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class SendFromRevoltError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class SendFromDiscordError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class SendFromGuildedError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class SentToNerimiryError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class SentToRevoltError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class SentToDiscordError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class SentToGuildedError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class DistributionError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    

class UpdateError(Exception):
    def __init__(self):
        pass

    class InvalidTokenError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class InvalidEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class ValidationError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class FaultyEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)


class SurrealDBHandler:

    class UpdateEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class CreateEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class DeleteEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class GetEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class EndpointNotFoundError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class SyncLocalFilesError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)


class ReadHandlerError:

    class MarkReadError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class InvalidPlatformError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class AlreadyReadError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)



class HealtCheckError:

    class EndpointCheckError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
        
        class EndpointConfigError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(self.message)
        
        class EndpointMetaDataError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(self.message)
