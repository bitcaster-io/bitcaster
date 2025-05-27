import logging
from typing import TYPE_CHECKING, Any

from .base import Dispatcher, MessageProtocol, Payload

if TYPE_CHECKING:
    from ..models import Assignment

logger = logging.getLogger(__name__)

MESSAGES = []


class BitcasterSysDispatcher(Dispatcher):
    id = 1
    slug = "test"
    local = True
    verbose_name = "Log"
    protocol = MessageProtocol.PLAINTEXT

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        from bitcaster.models.internal import LogMessage

        LogMessage.objects.create(level=address, application=payload.event.application, message=payload.message)
        return True
