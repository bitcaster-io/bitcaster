from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any
from unittest import mock

import freezegun
import pytest
from django.urls import reverse
from testutils.factories.attachment import AttachmentFactory

from bitcaster.utils.attachment import DownloadKeyManager

if TYPE_CHECKING:
    from django.test import Client
    from django_webtest import DjangoTestApp
    from pytest_django.fixtures import SettingsWrapper

    from bitcaster.models import User

pytestmark = pytest.mark.django_db


def test_home(client: "Client") -> None:
    assert client.get("/").status_code == 200


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


@freezegun.freeze_time(datetime(2025, 1, 1))
class TestAttachmentDownload:
    @pytest.mark.parametrize(
        "expires_at", [pytest.param(None, id="perpetual"), pytest.param(datetime(2026, 1, 1), id="fixed-time")]
    )
    def test_successful_download(self, django_app: DjangoTestApp, expires_at: datetime | None) -> None:
        attachment = AttachmentFactory()
        key = DownloadKeyManager().generate_key(attachment, expires_at)
        response = django_app.get(reverse("safe_download", kwargs={"key": key}))
        assert response.status_code == 200

    def test_bad_response_with_bogus_key(self, django_app: DjangoTestApp) -> None:
        response = django_app.get(reverse("safe_download", kwargs={"key": "THIS FAILS"}), expect_errors=True)
        assert response.status_code == 400

    def test_bad_response_with_expired_key(self, django_app: DjangoTestApp) -> None:
        attachment = AttachmentFactory()
        key = DownloadKeyManager().generate_key(attachment, expires_at=datetime(2020, 1, 1))
        response = django_app.get(reverse("safe_download", kwargs={"key": key}), expect_errors=True)
        assert response.status_code == 400

    def test_attachment_not_found(self, django_app: DjangoTestApp) -> None:
        # create an attachment, but don't save it...
        attachment = AttachmentFactory.build()
        # ... so we can generate a valid key with it...
        key = DownloadKeyManager().generate_key(attachment, expires_at=None)

        # ... and expect to find nothing in the db
        response = django_app.get(reverse("safe_download", kwargs={"key": key}), expect_errors=True)
        assert response.status_code == 404
