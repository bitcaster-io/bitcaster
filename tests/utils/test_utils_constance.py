from typing import TYPE_CHECKING, Any

from bitcaster.utils.constance import EmailChannel

if TYPE_CHECKING:
    from bitcaster.models import Channel


def test_emailchannel(db: Any, email_channel: "Channel") -> None:
    fld = EmailChannel()
    assert fld.choices == [(email_channel.pk, email_channel.name)]
