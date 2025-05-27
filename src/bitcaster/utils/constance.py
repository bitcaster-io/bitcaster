import logging
from typing import Any

from django.forms import ChoiceField

from bitcaster.dispatchers.base import MessageProtocol
from bitcaster.models import Channel

logger = logging.getLogger(__name__)


class EmailChannel(ChoiceField):
    def __init__(self, **kwargs: Any) -> None:
        ret = [
            (c["pk"], c["name"])
            for c in Channel.objects.values("pk", "name", "protocol")
            if c["protocol"] == MessageProtocol.EMAIL
        ]
        kwargs["choices"] = ret
        super().__init__(**kwargs)


class GroupSelect(ChoiceField):
    def __init__(self, **kwargs: Any) -> None:
        from django.contrib.auth.models import Group

        ret: list[tuple[str | int, str]] = [(c["name"], c["name"]) for c in Group.objects.values("pk", "name")]
        kwargs["choices"] = ret
        super().__init__(**kwargs)
