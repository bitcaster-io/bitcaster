from typing import TYPE_CHECKING, Any

import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers import EmailDispatcher

if TYPE_CHECKING:
    from bitcaster.models import Channel, MessageTemplate


@pytest.fixture
def email_channel(db: Any) -> "Channel":
    from testutils.factories.channel import ChannelFactory

    return ChannelFactory(dispatcher=fqn(EmailDispatcher))


@pytest.fixture
def email_message(email_channel: "Channel") -> "MessageTemplate":
    from testutils.factories import MessageTemplateFactory

    return MessageTemplateFactory(channel=email_channel)


def test_instantiate(message: "MessageTemplate", channel: "Channel") -> None:
    m = message.clone(channel)
    assert m.channel == channel
    assert m.event == message.event
    assert m.id != message.id


@pytest.mark.parametrize("args", [{}, {"application": None}, {"project": None, "application": None}])
def test_natural_key(args: dict[str, Any]) -> None:
    from testutils.factories import MessageTemplateFactory

    from bitcaster.models import MessageTemplate

    msg: "MessageTemplate" = MessageTemplateFactory.create(**args)
    assert MessageTemplate.objects.get_by_natural_key(*msg.natural_key()) == msg, msg.natural_key()
