from typing import TypedDict

PushConfig = TypedDict(
    "PushConfig",
    {
        "application_id": str,
        "registration_id": str,
        "browser": str,
        "auth": str,
        "p256dh": str,
    },
)
