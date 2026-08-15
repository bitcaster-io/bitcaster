from typing import TYPE_CHECKING

from datetime import datetime

if TYPE_CHECKING:
    from bitcaster.models.mixins import LockMixin


class AttachmentsNotSupportedError(Exception):
    pass


class ConfigError(Exception):
    pass


class DispatcherError(Exception):
    pass


class InvalidGrantError(Exception):
    pass


class InvalidOriginError(Exception):
    pass


class AgentError(Exception):
    pass


class LockError(Exception):
    def __init__(self, locked: "LockMixin"):
        self.locked = locked

    def __str__(self) -> str:
        return f"Unable to process this event. {self.locked.__class__.__name__} locked"


class InactiveError(Exception):
    def __init__(self, event: "LockMixin"):
        self.event = event

    def __str__(self) -> str:
        return f"Unable to accept this event. {self.event.__class__.__name__} is paused or deactivated"


class UnrelatedEventError(Exception):
    pass


class DecryptionError(Exception):
    pass


class KeyExpiredError(Exception):
    def __init__(self, expired_at: datetime):
        self.expired_at = expired_at

    def __str__(self) -> str:
        return f"Key expired at {self.expired_at}"
