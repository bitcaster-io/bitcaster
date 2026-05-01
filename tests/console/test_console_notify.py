from typing import TYPE_CHECKING

import pytest
from testutils.factories import UserMessageFactory

from bitcaster.console.utils import get_users_to_notify, set_user_latest_notify_time

if TYPE_CHECKING:  # pragma: no cover
    from bitcaster.models import UserMessage

pytestmark = [pytest.mark.xdist_group(name="console_notify")]


def create_message(**kwargs) -> "UserMessage":
    return UserMessageFactory.create(**kwargs)


@pytest.mark.django_db
def test_get_users_to_notify():
    # do not user fixture to create UserMessage, because we are emulating time elapse
    msg1: "UserMessage" = create_message()
    users = get_users_to_notify()
    assert users == [msg1.user.pk]  # New message need to be notified

    set_user_latest_notify_time(msg1.user.pk)
    users = get_users_to_notify()
    assert users == []  # Old messaged read. not need notification

    msg2: "UserMessage" = create_message()

    users = get_users_to_notify()
    assert users == [msg2.user.pk]  # Different user needs to be notified

    msg3: "UserMessage" = create_message(user=msg1.user)
    assert msg1.user.pk == msg3.user.pk  # New message for old same user needs to be notified

    users = get_users_to_notify()
    assert sorted(users) == [msg1.user.pk, msg2.user.pk]
