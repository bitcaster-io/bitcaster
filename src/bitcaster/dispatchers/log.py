from .base import Dispatcher, MessageProtocol, Payload

MESSAGES = []


class BitcasterLogDispatcher(Dispatcher):
    id = 1
    slug = "test"
    local = True
    verbose_name = "Log"
    protocol = MessageProtocol.PLAINTEXT

    def send(self, address: str, payload: Payload) -> bool:
        from bitcaster.models.log import LogMessage

        LogMessage.objects.create(level=address, application=payload.event.application, message=payload.message)
        return True
