from typing import TYPE_CHECKING

import pytest
from testutils.factories import DistributionListFactory, NotificationFactory

from bitcaster.forms.notification import NotificationForm
from bitcaster.models.choices import FILTERING_NONE

if TYPE_CHECKING:
    from bitcaster.models import Event, Notification

pytestmark = [pytest.mark.forms, pytest.mark.django_db]


def test_notification_form_rejects_pinned_dl_from_different_app() -> None:
    notification: "Notification" = NotificationFactory()
    other_event: "Event" = NotificationFactory(event__application__project=notification.event.application.project).event
    other_dl = DistributionListFactory(project=other_event.application.project, application=other_event.application)
    form = NotificationForm(
        instance=notification,
        data={
            "name": notification.name,
            "event": notification.event.pk,
            "distribution": other_dl.pk,
            "policy": FILTERING_NONE,
            "active": True,
        },
    )
    assert not form.is_valid()
    assert "distribution" in form.errors


def test_notification_form_accepts_pinned_dl_from_same_app() -> None:
    notification: "Notification" = NotificationFactory()
    event: "Event" = notification.event
    dl = DistributionListFactory(project=event.application.project, application=event.application)
    form = NotificationForm(
        instance=notification,
        data={
            "name": notification.name,
            "event": notification.event.pk,
            "distribution": dl.pk,
            "policy": FILTERING_NONE,
            "active": True,
        },
    )
    assert form.is_valid()


def test_notification_form_accepts_non_pinned_dl() -> None:
    notification: "Notification" = NotificationFactory()
    event: "Event" = notification.event
    dl = DistributionListFactory(project=event.application.project, application=None)
    form = NotificationForm(
        instance=notification,
        data={
            "name": notification.name,
            "event": notification.event.pk,
            "distribution": dl.pk,
            "policy": FILTERING_NONE,
            "active": True,
        },
    )
    assert form.is_valid()
