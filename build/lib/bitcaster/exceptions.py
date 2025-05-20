from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models.mixins import LockMixin


class DispatcherError(Exception):
    pass


class InvalidGrantError(Exception):
    pass


class LockError(Exception):
    def __init__(self, locked: "LockMixin"):
        self.locked = locked

    def __str__(self) -> str:
        return f"Unable to process this event. {self.locked.__class__.__name__} locked"
