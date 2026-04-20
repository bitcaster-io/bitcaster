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
