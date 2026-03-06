import base64
from datetime import datetime
from typing import TypedDict

import constance
from django.core.signing import Signer

from bitcaster.exceptions import DownloadKeyDecryptionError, DownloadKeyExpiredError
from bitcaster.models.attachment import Attachment

type DownloadKey = str


class KeyData(TypedDict):
    correlation_id: str
    expires_at: str


class DownloadKeyManager:
    """Creates and decrypts keys for use with attachments."""

    def __init__(self) -> None:
        """Create a key generator.

        The salt for key generation is set in Constance.

        Be aware that changing the salt will invalidate all valid
        download keys.
        """
        # TODO: get salt from constance
        self.salt = constance.config.ATTACHMENT_DOWNLOAD_KEY_SALT

    def generate_key(self, attachment: Attachment, expires_at: datetime | None = None) -> DownloadKey:
        """Generate a download key from the given `attachment`.

        The generated key is URL-safe.

        :param attachment: the attachment for message recipients to
            download
        :param expires_at: (optional) the `datetime` at which the key
            will stop being valid
        :return: the download key for the attachment
        """
        data: KeyData = {
            "correlation_id": attachment.correlation_id,
            "expires_at": datetime.isoformat(expires_at) if expires_at else "",
        }
        signed_data = Signer(salt=self.salt).sign_object(data).encode()

        return base64.urlsafe_b64encode(signed_data).decode().rstrip("=")

    def get_attachment(self, key: DownloadKey) -> Attachment:
        """Return the attachment for the given download `key`.

        :param key: the download key
        :raises DownloadKeyDecryptionError: the key could not be
            decrypted
        :raises DownloadKeyExpiredError: the key has been evaluated past
            its expiration date
        :return: an `Attachment` instance
        """
        padding = "=" * (4 - len(key) % 4)
        try:
            signed = base64.urlsafe_b64decode(key + padding).decode()
            data: KeyData = Signer(salt=self.salt).unsign_object(signed)
        except Exception as e:
            raise DownloadKeyDecryptionError(str(e)) from e

        formatted_expiration = data.get("expires_at")
        if formatted_expiration and datetime.now() > (expires_at := datetime.fromisoformat(formatted_expiration)):
            raise DownloadKeyExpiredError(expires_at)

        return Attachment.objects.get(correlation_id=data.get("correlation_id"))
