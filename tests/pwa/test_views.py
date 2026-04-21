from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from django.utils import timezone
from testutils.factories.usermessage import UserMessageFactory
from testutils.perms import configure_model

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp

    from bitcaster.models import User, UserMessage

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_message(user: User) -> "UserMessage":
    """User message fixture."""
    return UserMessageFactory.create(user=user)


@pytest.fixture
def user_messages(user: User) -> list["UserMessage"]:
    """User messages fixture for filtering tests."""
    return [
        UserMessageFactory.create(user=user, displayed=None, read=None),  # new
        UserMessageFactory.create(user=user, displayed=True, read=None),  # unread
        UserMessageFactory.create(user=user, read=timezone.now()),  # read
    ]


def test_pwa_index_anonymous(django_app: DjangoTestApp) -> None:
    response = django_app.get(reverse("pwa:index"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("pwa:login"))


def test_pwa_index_authenticated(django_app: DjangoTestApp, user: User) -> None:
    django_app.set_user(user)
    response = django_app.get(reverse("pwa:index"))
    assert response.status_code == 200


@pytest.mark.parametrize("status", ["new", "unread", "read", "all"])
def test_pwa_index_filtering(
    django_app: DjangoTestApp, user: User, user_messages: list[UserMessage], status: str
) -> None:
    django_app.set_user(user)
    response = django_app.get(reverse("pwa:index") + f"?status={status}")
    assert response.status_code == 200
    messages = response.context["messages"]
    if status == "new":
        assert all(m.displayed is None and m.read is None for m in messages)
    elif status == "unread":
        assert all(m.displayed is True and m.read is None for m in messages)
    elif status == "read":
        assert all(m.read is not None for m in messages)


def test_pwa_login(django_app: DjangoTestApp, user: User) -> None:
    response = django_app.get(reverse("pwa:login"))
    assert response.status_code == 200
    form = response.forms[0]
    form["username"] = user.username
    form["password"] = "password"
    response = form.submit()
    assert response.status_code == 302
    assert response.url.endswith(reverse("pwa:index"))


def test_pwa_logout(django_app: DjangoTestApp, user: User) -> None:
    django_app.set_user(user)
    response = django_app.get(reverse("pwa:logout"))
    assert response.status_code == 200
    response = response.form.submit()
    assert response.status_code == 302
    assert response.url.endswith(reverse("pwa:login"))


@pytest.mark.parametrize("read", [{"read", True}, {"read", False}])
@pytest.mark.parametrize("displayed", [{"displayed", None}, {"displayed", timezone.now()}])
def test_pwa_detail(django_app: DjangoTestApp, user: User, user_message: UserMessage, status, displayed) -> None:
    django_app.set_user(user)
    with configure_model(user_message, **{**displayed, **status}):
        response = django_app.get(reverse("pwa:detail", kwargs={"pk": user_message.pk}))
    assert response.status_code == 200
    assert response.context["message"] == user_message


def test_pwa_prefs(django_app: DjangoTestApp, user: User) -> None:
    django_app.set_user(user)
    response = django_app.get(reverse("pwa:prefs"))
    assert response.status_code == 200
    form = response.forms[0]
    form["timezone"] = "Europe/Rome"
    response = form.submit()
    assert response.status_code == 302
    user.refresh_from_db()
    assert str(user.timezone) == "Europe/Rome"


def test_pwa_serviceworker(django_app: DjangoTestApp) -> None:
    response = django_app.get(reverse("pwa:serviceworker"))
    assert response.status_code == 200
    assert response.content_type == "application/javascript"
    assert "Service-Worker-Allowed" in response.headers


def test_pwa_manifest(django_app: DjangoTestApp) -> None:
    response = django_app.get(reverse("pwa:manifest"))
    assert response.status_code == 200
    assert response.content_type == "application/manifest+json"


def test_pwa_offline(django_app: DjangoTestApp) -> None:
    response = django_app.get(reverse("pwa:offline"))
    assert response.status_code == 200
