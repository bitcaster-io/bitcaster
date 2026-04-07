import uuid
from typing import TYPE_CHECKING, TypedDict
from unittest import mock
from unittest.mock import Mock

import pytest
from django.contrib import messages
from django.db import connection
from django.test.utils import CaptureQueriesContext, override_settings
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from testutils.helpers import assert_message
from testutils.perms import user_grant_permissions

if TYPE_CHECKING:
    from webtest.response import TestResponse

    from bitcaster.models import (
        Assignment,
        Channel,
        DistributionList,
        Event,
        MessageTemplate,
        Notification,
        Occurrence,
        User,
    )

    Context = TypedDict(
        "Context",
        {
            "occurrence": Occurrence,
            "channel": Channel,
            "event": Event,
            "assignment": Assignment,
            "notification": Notification,
            "distribution": DistributionList,
            "message": MessageTemplate,
        },
    )


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


def _build_occurrence(status) -> "Context":
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        DistributionListFactory,
        EventFactory,
        MessageTemplateFactory,
        NotificationFactory,
        OccurrenceFactory,
    )

    ch = ChannelFactory.create()
    event = EventFactory.create(channels=[ch])
    asm: "Assignment" = AssignmentFactory.create(channel=ch)
    n = NotificationFactory.create(distribution__recipients=[asm], event=event)
    dl = DistributionListFactory.create(recipients=[asm])
    message = MessageTemplateFactory.create(event=event, channel=ch)
    return {
        "occurrence": OccurrenceFactory(event=n.event, status=status),
        "channel": ch,
        "event": event,
        "assignment": asm,
        "notification": n,
        "distribution": dl,
        "message": message,
    }


@pytest.fixture
def new_occurrence_data(app) -> "Context":
    from bitcaster.models import Occurrence

    return _build_occurrence(status=Occurrence.Status.NEW)


@pytest.fixture
def occurrence_data(app) -> "Context":
    from bitcaster.models import Occurrence

    return _build_occurrence(status=Occurrence.Status.PROCESSED)


@pytest.fixture
def new_occurrence(new_occurrence_data) -> "Occurrence":
    return new_occurrence_data["occurrence"]


@pytest.fixture
def occurrence(occurrence_data) -> "Occurrence":
    return occurrence_data["occurrence"]


def test_purge_occurrence_permission(app: DjangoTestApp, user: "User") -> None:
    url = reverse("admin:bitcaster_occurrence_purge")

    res: "TestResponse" = app.get(url, expect_errors=True)
    assert res.status_code == 403

    with user_grant_permissions(user, ["bitcaster.delete_occurrence"]):
        res = app.get(url)
    assert res.status_code == 200


def test_purge_occurrence(app_for_admin: DjangoTestApp, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("bitcaster.runner.tasks.purge_occurrences.send", purge_occurrences_mock := Mock())

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
    app_for_admin: DjangoTestApp, monkeypatch: pytest.MonkeyPatch, new_occurrence: "Occurrence"
) -> None:
    url = reverse("admin:bitcaster_occurrence_change", args=[new_occurrence.pk])
    res: "TestResponse" = app_for_admin.get(url)

    with mock.patch("bitcaster.models.occurrence.Occurrence.process", return_value=0):
        res = res.click("Process", linkid="btn-process")
        res = res.forms["confirm-form"].submit().follow()

    assert_message(res, "Occurrence has been processed, but no recipients have been reached out", messages.WARNING)

    res: "TestResponse" = app_for_admin.get(url)
    with mock.patch("bitcaster.models.occurrence.Occurrence.process", return_value=1):
        res = res.click("Process", linkid="btn-process")
        res = res.forms["confirm-form"].submit().follow()
    assert_message(res, "Occurrence has been successfully processed", messages.SUCCESS)

    res: "TestResponse" = app_for_admin.get(url)
    with mock.patch("bitcaster.models.occurrence.Occurrence.process", side_effect=Exception):
        res = res.click("Process", linkid="btn-process")
        res = res.forms["confirm-form"].submit().follow()
    assert_message(res, "Error processing occurrence", messages.ERROR)


@pytest.mark.parametrize("remove", ["full", "messages", "channels", "recipients"])
def test_inspect_new_occurrence(
    app_for_admin: DjangoTestApp, monkeypatch: pytest.MonkeyPatch, new_occurrence_data: "Context", remove
) -> None:
    new_occurrence = new_occurrence_data["occurrence"]
    url = reverse("admin:bitcaster_occurrence_change", args=[new_occurrence.pk])
    match remove:
        case "messages":
            new_occurrence_data["message"].delete()
        case "channels":
            new_occurrence_data["channel"].delete()
        case "recipients":
            new_occurrence_data["assignment"].delete()

    with override_settings(CACHE_PREFIX=uuid.uuid4().hex):
        res: "TestResponse" = app_for_admin.get(url)
        res = res.click("Inspect")
        with CaptureQueriesContext(connection) as ctx1:
            res = res.forms["confirm-form"].submit()
        assert res.status_code == 200
        assert "This occurrence has not been processed yet." in res.text, res.showbrowser()

        res: "TestResponse" = app_for_admin.get(url)
        res = res.click("Inspect")
        with CaptureQueriesContext(connection) as ctx2:
            res = res.forms["confirm-form"].submit()
        assert res.status_code == 200
        assert "This occurrence has not been processed yet." in res.text, res.showbrowser()
        assert len(ctx2) <= len(ctx1)  # check the cache


@pytest.mark.parametrize("remove", ["full", "messages", "channels", "recipients"])
def test_inspect_occurrence(
    app_for_admin: DjangoTestApp, monkeypatch: pytest.MonkeyPatch, occurrence_data: "Context", remove
) -> None:
    occurrence = occurrence_data["occurrence"]
    match remove:
        case "messages":
            occurrence_data["message"].delete()
        case "channels":
            occurrence_data["channel"].delete()
        case "recipients":
            occurrence_data["assignment"].delete()

    url = reverse("admin:bitcaster_occurrence_change", args=[occurrence.pk])
    with CaptureQueriesContext(connection) as ctx1:
        res: "TestResponse" = app_for_admin.get(url)
        res = res.click("Inspect")
    assert res.status_code == 200
    assert "This occurrence has already been processed" in res.text

    with CaptureQueriesContext(connection) as ctx2:
        res: "TestResponse" = app_for_admin.get(url)
        res = res.click("Inspect")
    assert res.status_code == 200
    assert len(ctx2) < len(ctx1)  # check the cache


def test_button_add_notification(
    app_for_admin: DjangoTestApp, monkeypatch: pytest.MonkeyPatch, occurrence: "Context"
) -> None:
    url = reverse("admin:bitcaster_occurrence_change", args=[occurrence.pk])
    res: "TestResponse" = app_for_admin.get(url)
    res = res.click("Add Notification")
    assert res
