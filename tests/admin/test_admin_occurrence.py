from typing import TYPE_CHECKING
from unittest import mock
from unittest.mock import Mock

import pytest
from django.contrib import messages
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from testutils.helpers import assert_message
from testutils.perms import user_grant_permissions

if TYPE_CHECKING:
    from webtest.response import TestResponse

    from bitcaster.models import Occurrence, User


@pytest.fixture
def app(django_app_factory: MixinWithInstanceVariables, user: "User") -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(user)
    django_app._user = user
    return django_app


@pytest.fixture
def app_for_admin(django_app_factory: MixinWithInstanceVariables, admin_user: "User") -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_purge_occurrence_permission(app: DjangoTestApp, user: "User") -> None:
    url = reverse("admin:bitcaster_occurrence_purge")

    res: "TestResponse" = app.get(url, expect_errors=True)
    assert res.status_code == 403

    with user_grant_permissions(user, ["bitcaster.delete_occurrence"]):
        res = app.get(url)
    assert res.status_code == 200


def test_purge_occurrence(app_for_admin: DjangoTestApp, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("bitcaster.tasks.purge_occurrences.delay", purge_occurrences_mock := Mock())

    url = reverse("admin:bitcaster_occurrence_purge")
    url_redirect = reverse("admin:bitcaster_occurrence_changelist")

    res: "TestResponse" = app_for_admin.get(url, headers={"REFERER": url_redirect})
    assert res.status_code == 200

    res = res.forms["confirm-form"].submit()
    assert res.location == url_redirect

    res = res.follow()
    assert res.status_code == 200
    assert "Occurrence purge has been successfully triggered" in res.text

    assert purge_occurrences_mock.called


def test_process_occurrence(
    app_for_admin: DjangoTestApp, monkeypatch: pytest.MonkeyPatch, occurrence: "Occurrence"
) -> None:
    url = reverse("admin:bitcaster_occurrence_change", args=[occurrence.pk])
    res: "TestResponse" = app_for_admin.get(url)

    with mock.patch("bitcaster.models.occurrence.Occurrence.process", return_value=0):
        res = res.click("Process")
        res = res.forms["confirm-form"].submit().follow()

    assert_message(res, "Occurrence has been processed, but no recipients have been reached out", messages.WARNING)

    res: "TestResponse" = app_for_admin.get(url)
    with mock.patch("bitcaster.models.occurrence.Occurrence.process", return_value=1):
        res = res.click("Process")
        res = res.forms["confirm-form"].submit().follow()
    assert_message(res, "Occurrence has been successfully processed", messages.SUCCESS)

    res: "TestResponse" = app_for_admin.get(url)
    with mock.patch("bitcaster.models.occurrence.Occurrence.process", side_effect=Exception):
        res = res.click("Process")
        res = res.forms["confirm-form"].submit().follow()
    assert_message(res, "Error processing occurrence", messages.ERROR)
