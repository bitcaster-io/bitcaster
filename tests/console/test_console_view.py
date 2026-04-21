from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from django.utils import timezone

if TYPE_CHECKING:
    from bitcaster.models import User, UserMessage

pytestmark = [pytest.mark.xdist_group(name="console_view")]


@pytest.fixture
def message() -> "UserMessage":
    from testutils.factories import UserMessageFactory

    return UserMessageFactory.create()


@pytest.fixture
def user_messages(user: "User") -> "list[UserMessage]":
    """User messages fixture for filtering tests."""
    from testutils.factories import UserMessageFactory

    return [
        UserMessageFactory.create(user=user, displayed=None, read=None),  # new
        UserMessageFactory.create(user=user, displayed=True, read=None),  # unread
        UserMessageFactory.create(user=user, read=timezone.now()),  # read
    ]


@pytest.mark.django_db
def test_console_index(django_app, message: "UserMessage") -> None:
    url: str = reverse("console:index")
    # First view: should be 'new'
    res = django_app.get(url, user=message.user)
    assert res.pyquery("span:contains('New')")

    # Second view: should no longer be 'new' but 'not read'
    res = django_app.get(url, user=message.user)
    assert not res.pyquery("span:contains('New')")
    assert res.pyquery("span:contains('Not Read')")


@pytest.mark.django_db
def test_console_detail(django_app, message: "UserMessage") -> None:
    # Ensure starting state is unread
    message.refresh_from_db()
    assert message.read is None

    url: str = reverse("console:detail", args=[message.pk])
    res = django_app.get(url, user=message.user)
    assert res.pyquery(f"div:contains('{message.subject}')")

    # Reload from database to verify side effect of viewing detail
    message.refresh_from_db()
    assert message.read is not None


@pytest.mark.django_db
def test_console_detail_already_read(django_app, message: "UserMessage") -> None:
    from django.utils import timezone

    message.read = timezone.now()
    message.save()

    url: str = reverse("console:detail", args=[message.pk])
    res = django_app.get(url, user=message.user)
    assert res.status_code == 200


@pytest.mark.django_db
def test_console_prefs(django_app, user) -> None:
    url: str = reverse("console:prefs")
    res = django_app.get(url, user=user)
    assert res.status_code == 200

    form = res.forms[0]
    form["timezone"] = "Europe/Rome"
    res = form.submit()
    assert res.status_code == 302
    user.refresh_from_db()
    assert str(user.timezone) == "Europe/Rome"


@pytest.mark.parametrize("status", ["unread", "read", "all"])
def test_pwa_index_filtering(django_app, user: "User", user_messages: "list[UserMessage]", status: str) -> None:
    django_app.set_user(user)
    response = django_app.get(reverse("console:index") + f"?status={status}")
    assert response.status_code == 200
    messages = response.context["messages"]
    if status == "unread":
        assert all(m.instance.read is None for m in messages)
    elif status == "read":
        assert all(m.instance.read is not None for m in messages)
