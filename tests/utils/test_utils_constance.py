from typing import Any

from bitcaster.models import Channel
from bitcaster.utils.constance import EmailChannel


def test_emailchannel(db: Any, channel: "Channel") -> None:
    fld = EmailChannel()
    assert fld.choices == [("", "None"), (channel.pk, channel.name)]
