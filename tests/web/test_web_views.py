from typing import TYPE_CHECKING, Any
from unittest import mock

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from pytest_django.fixtures import SettingsWrapper

from bitcaster.models import User

if TYPE_CHECKING:
    from django.test import Client

pytestmark = pytest.mark.django_db


def test_home(client: "Client") -> None:
    assert client.get("/").status_code == 200


def test_healthcheck(client: "Client") -> None:
    # DO NOT REVERSE THIS URL
    assert client.get("/healthcheck/").status_code == 200


def test_login(django_app: DjangoTestApp, user: "User") -> None:
    url = reverse("login")
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
    with mock.patch("bitcaster.web.views.was_modified_since", lambda *a: False):
        django_app.get(f"{settings.MEDIA_URL}/{resource}", expect_errors=True)
