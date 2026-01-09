import json
from typing import TYPE_CHECKING, Any, Optional

from django.core.cache import cache

from bitcaster.dispatchers.base import Dispatcher, Payload
from bitcaster.utils.json import smart_dumps

if TYPE_CHECKING:
    from bitcaster.models import Assignment, Channel


class XDispatcher(Dispatcher):  # type: ignore
    id = 1
    slug = "test"
    local = True
    verbose_name = "Test XDispatcher"
    text_message = True
    html_message = True

    def __init__(self, channel: "Channel") -> None:
        super().__init__(channel)
        self.client = cache.client

    @property
    def counter(self):
        return len(self.client.smembers(self.cache_key))

    @property
    def cache_key(self):
        seed = self.channel.config["seed"]
        return f"{seed}:messages"

    def send(self, address: str, payload: Payload, assignment: "Optional[Assignment]" = None, **kwargs: Any) -> bool:
        self.client.sadd(self.cache_key, smart_dumps([address, payload.message, self.counter]))
        return True

    def _messages(self) -> Any:
        return [json.loads(o) for o in (self.client.smembers(self.cache_key) or [])]
