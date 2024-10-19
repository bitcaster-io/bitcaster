from typing import TYPE_CHECKING, Any, Optional

from bitcaster.dispatchers.base import Dispatcher, Payload

if TYPE_CHECKING:
    from bitcaster.models import Assignment

MESSAGES = []


class XDispatcher(Dispatcher):  # type: ignore
    id = 1
    slug = "test"
    local = True
    verbose_name = "Test Dispatcher"
    text_message = True
    html_message = True

    def send(self, address: str, payload: Payload, assignment: "Optional[Assignment]" = None, **kwargs: Any) -> bool:
        MESSAGES.append((address, payload.message))
        return True
