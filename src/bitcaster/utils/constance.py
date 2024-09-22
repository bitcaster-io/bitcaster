import logging
from typing import Any

from django.forms import ChoiceField

from bitcaster.dispatchers.base import MessageProtocol
from bitcaster.models import Channel

logger = logging.getLogger(__name__)


class EmailChannel(ChoiceField):
    def __init__(self, **kwargs: Any) -> None:
        ret: list[tuple[str | int, str]] = [("", "None")]
        for c in Channel.objects.values("pk", "name", "protocol"):
            if c["protocol"] == MessageProtocol.EMAIL:
                ret.append((c["pk"], c["name"]))
        kwargs["choices"] = ret
        super().__init__(**kwargs)


class GroupSelect(ChoiceField):
    def __init__(self, **kwargs: Any) -> None:
        from django.contrib.auth.models import Group

        ret: list[tuple[str | int, str]] = []
        for c in Group.objects.values("pk", "name"):
            ret.append((c["name"], c["name"]))
        kwargs["choices"] = ret
        super().__init__(**kwargs)
