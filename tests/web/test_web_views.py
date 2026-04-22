from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from unittest import mock

import freezegun
import pytest
from django.urls import reverse
from testutils.factories.attachment import AttachmentFactory

from bitcaster.utils.security import KeyManager
from bitcaster.web.templatetags.attachments import attachment as attachment_tag

if TYPE_CHECKING:
    from django.test import Client
    from django_webtest import DjangoTestApp
    from pytest_django.fixtures import SettingsWrapper

    from bitcaster.models import Occurrence, User

pytestmark = pytest.mark.django_db


def test_home(client: "Client") -> None:
    assert client.get("/").status_code == 200


def test_home_mobile(client: "Client") -> None:
    iphone_ua = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
    )
    response = client.get("/", HTTP_USER_AGENT=iphone_ua)
    assert response.status_code == 302
    assert response.url == reverse("pwa:index")


def test_index_user_no_redirect(django_app: DjangoTestApp, user: "User") -> None:
    django_app.set_user(user)
    response = django_app.get(reverse("home"))
    assert response.status_code == 200


def test_healthcheck(client: "Client") -> None:
    # DO NOT REVERSE THIS URL
    assert client.get("/healthcheck/").status_code == 200


def test_login(django_app: DjangoTestApp, user: "User", settings: SettingsWrapper) -> None:
    settings.FLAGS = {"LOCAL_LOGIN": [("boolean", True)]}

    url = reverse("admin:login")
    res = django_app.get(url)
    assert res.status_code == 200

    res.form["username"] = user.username
    res.form["password"] = "--"
    res = res.form.submit()
    assert res.status_code == 200

    res.form["username"] = user.username
    res.form["password"] = "password"
    res = res.form.submit()
    assert res.status_code == 302


def test_logout(django_app: DjangoTestApp, user: "User") -> None:
    django_app.set_user(user)
    res = django_app.get("/")
    res = res.forms["logout-form"].submit()
    assert res.status_code == 302


@pytest.mark.parametrize("resource,expected", [("/", 404), ("logo.png", 200), ("invalid.txt", 404)])
def test_media(
    django_app: DjangoTestApp, user: "User", settings: SettingsWrapper, tmpdir: Any, resource: str, expected: int
) -> None:
    tmpdir.join("logo.png").write("content")
    settings.MEDIA_ROOT = tmpdir
    django_app.set_user(user)
    res = django_app.get(f"{settings.MEDIA_URL}/{resource}", expect_errors=True)
    assert res.status_code == expected
    with mock.patch("bitcaster.web.views.was_modified_since", return_value=False):
        django_app.get(f"{settings.MEDIA_URL}/{resource}", expect_errors=True)


@pytest.mark.parametrize("expires_at", [pytest.param(None, id="perpetual"), pytest.param(1, id="fixed-time")])
def test_successful_download(django_app: DjangoTestApp, expires_at: datetime | None) -> None:
    attachment = AttachmentFactory()
    url = attachment_tag({"address": "", "event": None}, attachment.correlation_id, 1)
    response = django_app.get(url)
    assert response.status_code == 200


def test_bad_response_with_bogus_key(django_app: DjangoTestApp) -> None:
    response = django_app.get(reverse("safe_download", kwargs={"key": "THIS FAILS"}), expect_errors=True)
    assert response.status_code == 400


def test_bad_response_with_expired_key(django_app: DjangoTestApp) -> None:
    attachment = AttachmentFactory()
    with freezegun.freeze_time(datetime(2025, 1, 1)):
        url = attachment_tag({"address": "", "event": None}, attachment.correlation_id, 1)

    response = django_app.get(url, expect_errors=True)
    assert response.status_code == 400


def test_attachment_not_found(django_app: DjangoTestApp) -> None:
    # create an attachment, but don't save it...
    attachment = AttachmentFactory.build()
    # ... so we can generate a valid key with it...
    key = KeyManager().generate_key(None, correlation_id=attachment.correlation_id)

    # ... and expect to find nothing in the db
    response = django_app.get(reverse("safe_download", kwargs={"key": key}), expect_errors=True)
    assert response.status_code == 404


def test_recipients_view(django_app: DjangoTestApp, occurrence: "Occurrence") -> None:
    key = KeyManager().generate_key(None, occurrence=occurrence.pk)
    url = reverse("recipients", kwargs={"token": key})
    response = django_app.get(url)
    assert response.status_code == 200
    assert response.context["occurrence"] == occurrence
