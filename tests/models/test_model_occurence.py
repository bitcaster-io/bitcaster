from typing import TYPE_CHECKING, List, TypedDict
from unittest.mock import Mock

import pytest

if TYPE_CHECKING:
    from pytest import MonkeyPatch

    from bitcaster.models import Assignment, Notification, Occurrence, User

    Context = TypedDict(
        "Context",
        {"assignment": Assignment, "notification": Notification},
    )


@pytest.fixture
def context(occurrence: "Occurrence", user: "User") -> "Context":
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        NotificationFactory,
    )

    notification: "Notification" = NotificationFactory(event__channels=[ChannelFactory()], payload_filter="foo=='bar'")
    assignment: "Assignment" = AssignmentFactory(channel=notification.event.channels.first())
    notification.distribution.recipients.add(assignment)

    return {"assignment": assignment, "notification": notification}


@pytest.mark.parametrize(
    "payload, notified_count",
    [pytest.param({"foo": "bar"}, 1, id="matched"), pytest.param({"foo": "dummy"}, 0, id="unmatched")],
)
@pytest.mark.django_db(transaction=True)
def test_model_occurrence_filter(
    payload: dict[str, str], notified_count: int, context: "Context", monkeypatch: "MonkeyPatch"
) -> None:
    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", mock := Mock())

    occurrence: Occurrence = context["notification"].event.trigger(payload)
    occurrence.process()

    assert mock.call_count == notified_count
    occurrence.refresh_from_db()

    if notified_count == 1:
        assert occurrence.data == {
            "delivered": [context["assignment"].id],
            "recipients": [[context["assignment"].address.value, context["assignment"].channel.name]],
        }


def test_model_occurrence_no_notifications(occurrence: "Occurrence", monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr("bitcaster.models.notification.Notification.get_context", mock := Mock())
    assert occurrence.process() is True
    assert mock.called is False


def test_str(occurrence: "Occurrence") -> None:
    assert str(occurrence)


def test_natural_key(occurrence: "Occurrence") -> None:
    from bitcaster.models import Occurrence

    assert Occurrence.objects.get_by_natural_key(*occurrence.natural_key()) == occurrence


def test_purgeable(purgeable_occurrences: List["Occurrence"], non_purgeable_occurrences: List["Occurrence"]) -> None:
    from bitcaster.models import Occurrence

    assert Occurrence.objects.count() == len(purgeable_occurrences) + len(non_purgeable_occurrences)  # Sanity check

    purgeable_occurrence_ids = Occurrence.objects.purgeable().order_by("id").values_list("id", flat=True)

    assert (list(purgeable_occurrence_ids) == sorted([o.id for o in purgeable_occurrences]))
