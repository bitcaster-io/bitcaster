from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from bitcaster.models import Channel, Message


class CreateMessage(Protocol):
    name: str

    def create_message(
        self, name: str, channel: "Channel", defaults: dict[str, Any] | None = None
    ) -> "Message":  # pragma: no cover
        ...
