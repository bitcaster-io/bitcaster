from typing import Any, Optional, Protocol

from bitcaster.models import Channel, Message


class CreateMessage(Protocol):
    def create_message(
        self, name: str, channel: "Channel", defaults: Optional[dict[str, Any]] = None
    ) -> "Message":  # pragma: no cover
        ...
