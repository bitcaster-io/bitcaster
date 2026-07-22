from typing import TYPE_CHECKING

import uuid

import pytest

from bitcaster.constants import bitcaster

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, Notification, Occurrence


def test_event_trigger(event: "Event") -> None:
    assert event.trigger(context={})


@pytest.mark.parametrize(
    "cid",
    [
        uuid.UUID("3f430b9b-ca28-43a3-bad0-954d20f35c37"),
        "cf09bfc574554e3a9619a69021936bcb",
        "ffe1b3e8-0fcd-42b5-8ccd-7304715b329d",
    ],
)
def test_trigger_correlation_id(event: "Event", cid: str) -> None:
    o: "Occurrence" = event.trigger(context={}, options={}, cid=cid)
    assert o.correlation_id == str(cid)


def test_get_trigger_url(event: "Event") -> None:
    assert event.get_trigger_url()


def test_event_notifications(event: "Event") -> None:
    from testutils.factories import AssignmentFactory, NotificationFactory

    ch: "Channel" = event.channels.first()
    n1: Notification = NotificationFactory.create(
        distribution__recipients=[AssignmentFactory.create(channel=ch) for __ in range(2)], event=event
    )
    n2 = NotificationFactory(distribution__recipients=[AssignmentFactory(channel=ch) for __ in range(2)], event=event)
    assert {n.pk for n in event.notifications.match({})} == {n1.pk, n2.pk}


def test_delete_event_protect_internal() -> None:
    from testutils.factories import EventFactory

    from bitcaster.models import Event

    event: Event = EventFactory.create()
    internal_event: Event = EventFactory.create(
        application__name=bitcaster.APPLICATION,
        application__project__name=bitcaster.PROJECT,
        application__project__organization__name=bitcaster.ORGANIZATION,
    )
    event.delete()
    internal_event.delete()

    assert not Event.objects.filter(pk=event.pk).exists()
    assert Event.objects.filter(pk=internal_event.pk).exists()
