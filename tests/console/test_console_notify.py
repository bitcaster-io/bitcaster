from typing import TYPE_CHECKING

import pytest

from bitcaster.console.utils import get_users_to_notify, set_user_latest_notify_time

if TYPE_CHECKING:
    from bitcaster.models import UserMessage


@pytest.mark.django_db
def test_get_users_to_notify():
    from testutils.factories import UserMessageFactory

    msg1: "UserMessage" = UserMessageFactory.create()
    users = get_users_to_notify()
    assert users == [msg1.user.pk]  # New message need to be notified

    set_user_latest_notify_time(msg1.user.pk)
    users = get_users_to_notify()
    assert users == []  # Old messaged read. not need notification

    msg2: "UserMessage" = UserMessageFactory.create()
    users = get_users_to_notify()
    assert users == [msg2.user.pk]  # Different user needs to be notified

    msg3: "UserMessage" = UserMessageFactory.create(user=msg1.user)
    assert msg1.user.pk == msg3.user.pk  # New message for old same user needs to be notified

    users = get_users_to_notify()
    assert sorted(users) == [msg1.user.pk, msg2.user.pk]
