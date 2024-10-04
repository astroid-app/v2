
# This file contains all the custom exceptions that are raised in the api or during handling.
# The exceptions are divided into different classes based on the module they are raised in.
# Exceptions listed here aren't handeled yet. Currently they are just for raising and logging purposes.
# This will be updated and exceptions will be handeled in the future.


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
    
    class CreateIncidentError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class GetIncidentError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class UpdateIncidentError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class DeleteIncidentError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class ListIncidentsError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class GetStatusError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class UpdateStatusError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class CreateAttachmentError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class UpdateAttachmentError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class DeleteAttachmentError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class GetAttachmentError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class CheckEligibilityError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class ProfileNotFoundError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class ProfileCreationError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class ProfileUpdateError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class ProfileDeletionError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class GetProfileError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class GetStatisticsError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    

    class GetSuspensionStatusError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class SuspendEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class UnsuspendEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class GetSuspensionError(Exception):
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

class AttachmentProcessError:
    class AttachmentDownloadError:
        class AttachmentNotFound(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(self.message)

        class AttachmentDownloadError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(self.message)

        class AttachmentTooLarge(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(self.message)

    class AttachmentClearError:
        class DeletionError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(self.message)
    
    

class ProfileProcessorError:
    class ProfileNotFoundError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)


class SuspensionHandlerError:

    class GetSuspensionStatusError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)
    
    class SuspendEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)

    class UnsuspendEndpointError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)