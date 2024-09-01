import uuid
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, Occurrence


def test_event_trigger(event: "Event") -> None:
    assert event.trigger({})


@pytest.mark.parametrize(
    "cid",
    [
        uuid.UUID("3f430b9b-ca28-43a3-bad0-954d20f35c37"),
        "cf09bfc574554e3a9619a69021936bcb",
        "ffe1b3e8-0fcd-42b5-8ccd-7304715b329d",
    ],
)
def test_trigger_correlation_id(event: "Event", cid: str) -> None:
    o: "Occurrence" = event.trigger({}, options={}, cid=cid)
    assert o.correlation_id == str(cid)


def test_event_notifications(event: "Event") -> None:
    from testutils.factories import AssignmentFactory, NotificationFactory

    from bitcaster.models import Notification

    ch: "Channel" = event.channels.first()
    n1: Notification = NotificationFactory(
        distribution__recipients=[AssignmentFactory(channel=ch) for __ in range(2)], event=event
    )
    n2 = NotificationFactory(distribution__recipients=[AssignmentFactory(channel=ch) for __ in range(2)], event=event)
    assert list(event.notifications.match({})) == [n1, n2]
