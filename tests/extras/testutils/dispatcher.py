from bitcaster.dispatchers.base import Dispatcher, Payload

MESSAGES = []


class TDispatcher(Dispatcher):
    id = 1
    slug = "test"
    local = True
    verbose_name = "Test Dispatcher"
    text_message = True
    html_message = True

    def send(self, address: str, payload: Payload) -> None:
        MESSAGES.append((address, payload.message))
