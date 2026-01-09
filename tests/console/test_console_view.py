from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from bitcaster.models import UserMessage


@pytest.fixture
def message() -> "UserMessage":
    from testutils.factories import UserMessageFactory

    return UserMessageFactory.create()


@pytest.mark.django_db
def test_console_index(django_app, message: "UserMessage"):
    url = reverse("console:index")
    res = django_app.get(url, user=message.user)
    assert res.pyquery("tr td:contains('new')")

    res = django_app.get(url, user=message.user)
    assert not res.pyquery("tr td:contains('new')")
    assert res.pyquery("tr td:contains('not read')")


@pytest.mark.django_db
def test_console_detail(django_app, message: "UserMessage"):
    assert message.read is None
    url = reverse("console:detail", args=[message.pk])
    res = django_app.get(url, user=message.user)
    assert res.pyquery(f"div:contains('{message.subject}')")
    message.refresh_from_db()
    assert message.read
