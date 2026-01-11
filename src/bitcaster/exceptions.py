from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models.mixins import LockMixin


class ConfigError(Exception):
    pass


class DispatcherError(Exception):
    pass


class InvalidGrantError(Exception):
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
