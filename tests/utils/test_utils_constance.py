from typing import Any

from bitcaster.models import Channel
from bitcaster.utils.constance import EmailChannel


def test_emailchannel(db: Any, email_channel: "Channel") -> None:
    fld = EmailChannel()
    assert fld.choices == [(email_channel.pk, email_channel.name)]
