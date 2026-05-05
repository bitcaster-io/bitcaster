from typing import Any

import freezegun

from strategy_field.utils import fqn

from bitcaster.dispatchers import UserMessageDispatcher


def test_usermessage_get_by_natural_key(db: Any) -> None:
    from testutils.factories import UserMessageFactory

    from bitcaster.models import UserMessage

    msg = UserMessageFactory.create()
    assert UserMessage.objects.get_by_natural_key(*msg.natural_key())


def test_usermessage_manager_expired(db: Any) -> None:
    from testutils.factories import ChannelFactory, UserMessageFactory

    from bitcaster.models import UserMessage

    ChannelFactory(config={"message_ttl": 1}, dispatcher=fqn(UserMessageDispatcher))
    with freezegun.freeze_time("2000-01-01 00:00:00"):
        UserMessageFactory.create()
    assert UserMessage.objects.expired().count() == 1


def test_usermessage_manager_active(db: Any) -> None:
    from testutils.factories import ChannelFactory, UserMessageFactory

    from bitcaster.models import UserMessage

    ChannelFactory(config={"message_ttl": 1}, dispatcher=fqn(UserMessageDispatcher))
    with freezegun.freeze_time("2000-01-01 00:00:00"):
        UserMessageFactory.create()
        assert UserMessage.objects.active().count() == 1


def test_usermessage_manager_no_channel(db: Any) -> None:
    from testutils.factories import UserMessageFactory

    from bitcaster.models import UserMessage

    UserMessageFactory.create()
    assert UserMessage.objects.active()
    assert not UserMessage.objects.expired()
