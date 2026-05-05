from typing import Any

import base64
from datetime import datetime, timedelta

import constance
from flags.state import flag_enabled

from django.conf import settings
from django.core.signing import Signer

from bitcaster.exceptions import DecryptionError, KeyExpiredError


def is_root(request: Any, *args: Any, **kwargs: Any) -> bool:
    return settings.DEBUG and flag_enabled("IS_ROOT", request=request)


class KeyManager:
    def __init__(
        self,
    ) -> None:
        self.salt = constance.config.SECRET_KEY_SALT

    def generate_key(self, ttl: int | None = None, **kwargs: Any) -> str:
        if not ttl:
            expiration = None
        else:
            expiration = datetime.now() + timedelta(days=abs(ttl))
        data = {
            "expires_at": datetime.isoformat(expiration) if expiration else "",
            **kwargs,
        }
        signed_data = Signer(salt=self.salt).sign_object(data).encode()

        return base64.urlsafe_b64encode(signed_data).decode().rstrip("=")

    def parse_key(self, key: str) -> dict[str, str | int]:
        padding = "=" * (4 - len(key) % 4)
        try:
            signed = base64.urlsafe_b64decode(key + padding).decode()
            data = Signer(salt=self.salt).unsign_object(signed)
            formatted_expiration = data.get("expires_at")
            if formatted_expiration and datetime.now() > (expires_at := datetime.fromisoformat(formatted_expiration)):
                raise KeyExpiredError(expires_at)
        except KeyExpiredError as e:
            raise e
        except Exception as e:
            raise DecryptionError(str(e)) from e
        return data
