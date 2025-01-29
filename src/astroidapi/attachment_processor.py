import requests
import astroidapi.errors as errors
import astroidapi.surrealdb_handler as surrealdb_handler
import pathlib
import random
import pathlib
import string

async def download_attachment(attachment_url, registeredPlatforms):
    try: 
        response = requests.get(attachment_url)
        if response.status_code == 200:
            try:
                content_length = response.headers["content-length"]
                if int(response.headers["content-length"]) > 50 * 1024 * 1024: # value in B -> KB -> MB
                    raise errors.AttachmentProcessError.AttachmentDownloadError.AttachmentTooLarge("Attachment is too large. Maximum size is 50MB.")
            except KeyError:
                content_length = len(response.content)
                if content_length > 50 * 1024 * 1024:
                    raise errors.AttachmentProcessError.AttachmentDownloadError.AttachmentTooLarge("Attachment is too large. Maximum size is 50MB.")
            print(f"Downloading attachment from {attachment_url}. Size: {int(content_length) / 1024 }KB")
            id_chars = string.ascii_lowercase + string.digits
            attachment_id = "".join(random.choices(id_chars, k=16))
            attachment_name = attachment_url.split('/')[-1]
            attachment_type = attachment_name.split('.')[-1]
            if "?" in attachment_type:
                attachment_type = attachment_type.split("?")[0]
            elif "%3F" in attachment_type:
                attachment_type = attachment_type.split("%3F")[0]
            await surrealdb_handler.AttachmentProcessor.create_attachment(attachment_id, status="downloading", type=attachment_type, registeredPlatforms=registeredPlatforms)
            attachment = response.content
            attachment_path = f"{pathlib.Path(__file__).parent.resolve()}/TMP_attachments/{attachment_id}.{attachment_type}"
            if '../' in attachment_path or '..\\' in attachment_path:
                raise Exception("Invalid file path")
            with open(attachment_path, 'wb') as file:
                file.write(attachment)
                file.close()
                await surrealdb_handler.AttachmentProcessor.update_attachment(attachment_id, status="downloaded")
            return file
        if response.status_code == 404:
            print(f"Attachment not found. Statuscode: {response.status_code}")
            return None
        else:
            raise errors.AttachmentProcessError.AttachmentDownloadError.AttachmentDownloadError(f"Received invalid Statuscode. Statuscode: {response.status_code}")
    except Exception as e:
        raise errors.AttachmentProcessError.AttachmentDownloadError.AttachmentDownloadError(f"Error downloading attachment. Error: {e}")
    

async def clear_temporary_attachments():
    try:
        path = f"{pathlib.Path(__file__).parent.resolve()}/TMP_attachments"
        for file in pathlib.Path(path).iterdir():
            if file.name == ".placeholder":
                continue
            print(f"Checking attachment: {file.name}")
            attachmend_id = file.name.split('.')[0]
            await check_attachment(attachmend_id)
            attachment = await surrealdb_handler.AttachmentProcessor.get_attachment(attachmend_id)
            print(f"Attachment status: {attachment['status']}")
            try:
                if attachment["status"] == "sent" or attachment["status"] == "canDelete":
                    file.unlink()
                    await surrealdb_handler.AttachmentProcessor.delete_attachment(attachmend_id)
            except Exception as e:
                raise errors.AttachmentProcessError.AttachmentClearError.DeletionError(f"Error deleting temporary attachments. Error: {e}")
            
    except Exception as e:
        raise errors.AttachmentProcessError.AttachmentClearError.DeletionError(f"Error deleting temporary attachments. Error: {e}")

async def check_attachment(attachment_id):
    try:
        attachment = await surrealdb_handler.AttachmentProcessor.get_attachment(attachment_id)
        try:
            sentBy = attachment["sentBy"]
        except TypeError:
            return
        if sentBy["discord"] and sentBy["guilded"] and sentBy["revolt"] and sentBy["nerimity"]:
            await surrealdb_handler.AttachmentProcessor.update_attachment(attachment_id, status="canDelete")
            
    except Exception as e:
        raise errors.AttachmentProcessError.AttachmentDownloadError.AttachmentNotFound(f"Attachment not found. Error: {e}")

def clear_temporary_attachment(attachment_path):
    try:
        pathlib.Path(attachment_path.replace("\\", "/")).unlink()
    except Exception as e:
        raise errors.AttachmentProcessError.AttachmentClearError.DeletionError(f"Error deleting temporary attachment. Error: {e}")
    
async def force_clear_temporary_attachments():
    try:
        path = f"{pathlib.Path(__file__).parent.resolve()}/TMP_attachments"
        for file in pathlib.Path(path).iterdir():
            if file.name == ".placeholder":
                continue
            await surrealdb_handler.AttachmentProcessor.delete_attachment(file.name.split('.')[0])
            file.unlink()
    except Exception as e:
        raise errors.AttachmentProcessError.AttachmentClearError.DeletionError(f"Error deleting temporary attachments. Error: {e}")