from typing import TYPE_CHECKING, Any

import logging

from .base import Dispatcher, MessageProtocol, Payload

if TYPE_CHECKING:
    from ..models import Assignment

logger = logging.getLogger(__name__)

MESSAGES = []


class LocalDatabaseDispatcher(Dispatcher):
    id = 1
    slug = "log"
    local = True
    verbose_name = "Log"
    protocol = MessageProtocol.PLAINTEXT

    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        from bitcaster.models.internal import LogMessage

        LogMessage.objects.create(level=address, application=payload.event.application, message=payload.message)
        return True
