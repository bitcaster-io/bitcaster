import logging
from typing import TYPE_CHECKING, Any, Optional

from .base import Dispatcher, MessageProtocol, Payload

if TYPE_CHECKING:
    from ..models import Assignment

logger = logging.getLogger(__name__)

MESSAGES = []


class BitcasterLogDispatcher(Dispatcher):
    id = 1
    slug = "test"
    local = True
    verbose_name = "Log"
    protocol = MessageProtocol.PLAINTEXT

    def send(self, address: str, payload: Payload, assignment: "Optional[Assignment]" = None, **kwargs: Any) -> bool:
        from bitcaster.models.log import LogMessage

        LogMessage.objects.create(level=address, application=payload.event.application, message=payload.message)
        return True
