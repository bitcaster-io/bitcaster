from typing import Protocol, Optional, Any

from bitcaster.models import Channel, Message


class CreateMessage(Protocol):
    def create_message(self, name: str, channel: "Channel", defaults: Optional[dict[str, Any]] = None) -> "Message":
        ...
