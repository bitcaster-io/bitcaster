from typing import TYPE_CHECKING

from .base import Dispatcher, Payload

if TYPE_CHECKING:
    from bitcaster.models.log import LogMessage


MESSAGES = []


class BitcasterLogDispatcher(Dispatcher):
    id = 1
    slug = "test"
    local = True
    verbose_name = "Test Dispatcher"
    text_message = True
    html_message = True
    has_subject = False

    def send(self, address: str, payload: Payload) -> "LogMessage":
        from bitcaster.models.log import LogMessage

        return LogMessage.objects.create(level=address, application=payload.event.application, message=payload.message)
