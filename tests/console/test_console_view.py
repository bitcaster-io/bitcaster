from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from bitcaster.models import UserMessage

pytestmark = [pytest.mark.xdist_group(name="console_view")]


@pytest.fixture
def message() -> "UserMessage":
    from testutils.factories import UserMessageFactory

    return UserMessageFactory.create()


@pytest.mark.django_db
def test_console_index(django_app, message: "UserMessage") -> None:
    url: str = reverse("console:index")
    # First view: should be 'new'
    res = django_app.get(url, user=message.user)
    assert res.pyquery("tr td:contains('new')")

    # Second view: should no longer be 'new' but 'not read'
    res = django_app.get(url, user=message.user)
    assert not res.pyquery("tr td:contains('new')")
    assert res.pyquery("tr td:contains('not read')")


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
