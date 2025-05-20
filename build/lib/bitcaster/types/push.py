from typing import TypedDict


class PushConfig(TypedDict):
    application_id: str
    registration_id: str
    browser: str
    auth: str
    p256dh: str
