from unittest import mock

import pytest
from django.urls import reverse


def test_home(db, client):
    assert client.get("/").status_code == 200


def test_login(db, django_app, user):
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


def test_logout(db, django_app, user):
    django_app.set_user(user)
    res = django_app.get("/")
    res = res.forms["logout-form"].submit()
    assert res.status_code == 302


@pytest.mark.parametrize("resource,expected", [("/", 404), ("logo.png", 200), ("invalid.txt", 404)])
def test_media(db, django_app, user, settings, tmpdir, resource, expected):
    tmpdir.join("logo.png").write("content")
    settings.MEDIA_ROOT = tmpdir
    django_app.set_user(user)
    res = django_app.get(f"{settings.MEDIA_URL}/{resource}", expect_errors=True)
    assert res.status_code == expected
    with mock.patch("bitcaster.web.views.was_modified_since", lambda *a: False):
        django_app.get(f"{settings.MEDIA_URL}/{resource}", expect_errors=True)
