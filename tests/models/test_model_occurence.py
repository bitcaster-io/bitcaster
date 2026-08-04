# mypy: disable-error-code="attr-defined"
from typing import TYPE_CHECKING, Any, List, TypedDict

import datetime

import pytest
from freezegun import freeze_time
from freezegun.api import FakeDatetime
from unittest.mock import Mock

if TYPE_CHECKING:
    from bitcaster.models import Assignment, Notification, Occurrence, User

    Context = TypedDict(
        "Context",
        {"assignment": Assignment, "notification": Notification},
    )


@pytest.fixture
def context(occurrence: "Occurrence", user: "User") -> "Context":
    from testutils.factories import AssignmentFactory, ChannelFactory, MessageTemplateFactory, NotificationFactory

    notification: "Notification" = NotificationFactory.create(
        event__channels=[ChannelFactory()], payload_filter="foo=='bar'"
    )
    assignment: "Assignment" = AssignmentFactory.create(channel=notification.event.channels.first())
    MessageTemplateFactory(channel=assignment.channel, event=notification.event)
    notification.distribution.recipients.add(assignment)

    return {"assignment": assignment, "notification": notification}


@pytest.mark.parametrize(
    "payload, notified_count",
    [pytest.param({"foo": "bar"}, 1, id="matched"), pytest.param({"foo": "dummy"}, 0, id="unmatched")],
)
@pytest.mark.django_db(transaction=True)
def test_model_occurrence_filter(
    payload: dict[str, str], notified_count: int, context: "Context", monkeypatch: pytest.MonkeyPatch
) -> None:
    from bitcaster.models import Delivery

    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel", mock := Mock(return_value=(None, 999))
    )
    asm = context["assignment"]
    n = context["notification"]
    occurrence: Occurrence = context["notification"].event.trigger(context=payload)
    msg = n.get_message(asm.channel)
    occurrence.process()

    assert mock.call_count == 0  # Phase 1 never dispatches
    occurrence.refresh_from_db()

    if notified_count == 1:
        assert occurrence.data == {
            "channels": [asm.channel.pk],
            "messages": [msg.pk],
            "notifications": [context["notification"].pk],
            "delivered": [],
            "recipients": [
                [asm.address.value, asm.channel.name, asm.pk, asm.channel.pk, context["notification"].pk, msg.pk]
            ],
            "errors": [],
            "rendered": [
                {
                    "assignment_pk": asm.pk,
                    "notification_pk": context["notification"].pk,
                    "notification_name": context["notification"].name,
                    "channel_pk": asm.channel.pk,
                    "channel_name": asm.channel.name,
                    "address": asm.address.value,
                    "subject": "",
                    "message": f"Message for {occurrence.event.name} on channel {asm.channel.name}",
                    "html_message": "",
                }
            ],
            "missing_template": [],
            "processing": {
                "phase1_at": occurrence.data["processing"]["phase1_at"],
                "phase2_attempts": [],
            },
        }
        assert occurrence.recipients == 1
        assert occurrence.deliveries.count() == 1
        (delivery,) = occurrence.deliveries.all()
        assert delivery.status == Delivery.Status.PENDING
        assert delivery.message_template == msg
    else:
        assert occurrence.recipients == 0
        assert occurrence.deliveries.count() == 0


@pytest.mark.django_db(transaction=True)
def test_process_creates_delivery_with_rendered_snapshot(context: "Context") -> None:
    asm = context["assignment"]
    occurrence: Occurrence = context["notification"].event.trigger(context={"foo": "bar"})
    occurrence.process()
    occurrence.refresh_from_db()

    (delivery,) = occurrence.deliveries.all()
    assert delivery.rendered == {
        "subject": "",
        "message": f"Message for {occurrence.event.name} on channel {asm.channel.name}",
        "html_message": "",
    }
    assert delivery.assignment == asm
    assert delivery.channel == asm.channel
    assert delivery.notification == context["notification"]


@pytest.mark.django_db(transaction=True)
def test_process_missing_template_delivery(context: "Context") -> None:
    from bitcaster.models import Delivery, MessageTemplate, Occurrence

    MessageTemplate.objects.all().delete()
    occurrence: Occurrence = context["notification"].event.trigger(context={"foo": "bar"})
    occurrence.process()
    occurrence.refresh_from_db()

    assert occurrence.status == Occurrence.Status.PROCESSING
    assert occurrence.recipients == 1
    (delivery,) = occurrence.deliveries.all()
    assert delivery.message_template is None
    assert delivery.missing_template
    assert delivery.status == Delivery.Status.FAILURE
    assert delivery.data["missing_template"] is True


@pytest.mark.django_db(transaction=True)
def test_process_renders_content_snapshot(context: "Context") -> None:
    from testutils.factories import MessageTemplateFactory

    asm = context["assignment"]
    MessageTemplateFactory(
        channel=asm.channel,
        event=context["notification"].event,
        notification=context["notification"],
        content="Hello {{ foo }}",
    )
    occurrence: Occurrence = context["notification"].event.trigger(context={"foo": "bar"})
    occurrence.process()
    occurrence.refresh_from_db()

    (delivery,) = occurrence.deliveries.all()
    assert delivery.rendered["message"] == "Hello bar"


@pytest.mark.django_db(transaction=True)
def test_process_reprocessing_does_not_duplicate_deliveries(context: "Context") -> None:
    from bitcaster.models import Occurrence

    occurrence: Occurrence = context["notification"].event.trigger(context={"foo": "bar"})
    occurrence.process()
    occurrence.refresh_from_db()
    first_count = occurrence.deliveries.count()
    assert first_count == 1

    occurrence.status = Occurrence.Status.NEW
    occurrence.save()
    occurrence.process()
    occurrence.refresh_from_db()
    assert occurrence.deliveries.count() == first_count
    assert occurrence.recipients == first_count


def test_model_occurrence_no_notifications(occurrence: "Occurrence", monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("bitcaster.models.notification.Notification.get_context", mock := Mock())
    assert occurrence.process() == 0
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

    assert list(purgeable_occurrence_ids) == sorted([o.id for o in purgeable_occurrences])


@freeze_time("2001-01-02T01:02:33Z")
@pytest.mark.parametrize(
    "ctx, expected",
    [
        pytest.param({}, {}, id="all-empty"),
        pytest.param({"new": 123}, {"new": 123}, id="contribute"),
        pytest.param({"a": 1, "timestamp": 33, "c": 3}, {"a": 1, "c": 3}, id="override"),
    ],
)
def test_get_context(ctx: dict[str, str], expected: dict[str, Any]) -> None:
    from testutils.factories import OccurrenceFactory

    occurrence: Occurrence = OccurrenceFactory()
    occurrence.context = ctx

    expected = expected | {
        "occurrence": occurrence,
        "timestamp": FakeDatetime(2001, 1, 2, 1, 2, 33, tzinfo=datetime.timezone.utc),
        "event": occurrence.event,
    }

    assert occurrence.get_context() == expected


def test_preview_fast_no_side_effects(user: "User") -> None:
    from testutils.factories import AssignmentFactory, ChannelFactory, MessageTemplateFactory, NotificationFactory

    from bitcaster.models import Occurrence

    notification: "Notification" = NotificationFactory.create(event__channels=[ChannelFactory()])
    assignment: "Assignment" = AssignmentFactory.create(channel=notification.event.channels.first())
    msg = MessageTemplateFactory(channel=assignment.channel, event=notification.event)
    notification.distribution.recipients.add(assignment)

    occurrence = Occurrence(event=notification.event, context={"foo": "bar"}, options={})
    success, data = occurrence.preview("fast")

    assert success is True
    assert data["delivered"] == []
    assert data["recipients"] == [
        (
            assignment.address.value,
            assignment.channel.name,
            assignment.pk,
            assignment.channel.pk,
            notification.pk,
            msg.pk,
        )
    ]
    assert "rendered" not in data
    assert "missing_template" not in data
    assert Occurrence.objects.count() == 0  # no rows created


def test_preview_full_renders_all(user: "User") -> None:
    from testutils.factories import AssignmentFactory, ChannelFactory, MessageTemplateFactory, NotificationFactory

    from bitcaster.models import Occurrence

    notification: "Notification" = NotificationFactory.create(event__channels=[ChannelFactory()])
    assignment: "Assignment" = AssignmentFactory.create(channel=notification.event.channels.first())
    MessageTemplateFactory(channel=assignment.channel, event=notification.event, content="Hello {{ event.name }}")
    notification.distribution.recipients.add(assignment)

    occurrence = Occurrence(event=notification.event, context={"foo": "bar"}, options={})
    success, data = occurrence.preview("full")

    assert success is True
    assert data["delivered"] == []
    rendered = data["rendered"]
    assert len(rendered) == 1
    entry = rendered[0]
    assert entry["assignment_pk"] == assignment.pk
    assert entry["notification_pk"] == notification.pk
    assert entry["notification_name"] == notification.name
    assert entry["channel_pk"] == assignment.channel.pk
    assert entry["channel_name"] == assignment.channel.name
    assert entry["address"] == assignment.address.value
    assert entry["subject"] == ""
    assert entry["message"] == f"Hello {notification.event.name}"
    assert "html_message" in entry


def test_preview_partial_caps_rendering(user: "User") -> None:
    from testutils.factories import AssignmentFactory, ChannelFactory, MessageTemplateFactory, NotificationFactory

    from bitcaster.models import Occurrence

    notification: "Notification" = NotificationFactory.create(event__channels=[ChannelFactory()])
    channel = notification.event.channels.first()
    MessageTemplateFactory(channel=channel, event=notification.event)
    for i in range(5):
        asm: "Assignment" = AssignmentFactory.create(channel=channel, address__value=f"user{i}@example.com")
        notification.distribution.recipients.add(asm)

    occurrence = Occurrence(event=notification.event, context={"foo": "bar"}, options={})
    success, data = occurrence.preview("partial", limit=2)

    assert success is True
    assert len(data["recipients"]) == 5  # all recipients collected
    assert len(data["rendered"]) == 2  # rendering capped


def test_preview_missing_template(user: "User") -> None:
    from testutils.factories import AssignmentFactory, ChannelFactory, NotificationFactory

    from bitcaster.models import Occurrence

    notification: "Notification" = NotificationFactory.create(event__channels=[ChannelFactory()])
    assignment: "Assignment" = AssignmentFactory.create(channel=notification.event.channels.first())
    notification.distribution.recipients.add(assignment)

    occurrence = Occurrence(event=notification.event, context={"foo": "bar"}, options={})
    success, data = occurrence.preview("full")

    assert success is True
    assert data["recipients"][0][5] is None  # template_pk is None
    assert data["rendered"] == []
    assert data["missing_template"] == [
        {
            "address": assignment.address.value,
            "channel_name": assignment.channel.name,
            "assignment_pk": assignment.pk,
            "channel_pk": assignment.channel.pk,
            "notification_pk": notification.pk,
            "notification_name": notification.name,
        }
    ]


def test_preview_render_error_does_not_abort(user: "User", monkeypatch: pytest.MonkeyPatch) -> None:
    from testutils.factories import AssignmentFactory, ChannelFactory, MessageTemplateFactory, NotificationFactory

    from bitcaster.models import Occurrence

    notification: "Notification" = NotificationFactory.create(event__channels=[ChannelFactory()])
    channel = notification.event.channels.first()
    MessageTemplateFactory(channel=channel, event=notification.event)
    asm1: "Assignment" = AssignmentFactory.create(channel=channel, address__value="a@example.com")
    asm2: "Assignment" = AssignmentFactory.create(channel=channel, address__value="b@example.com")
    notification.distribution.recipients.add(asm1)
    notification.distribution.recipients.add(asm2)

    monkeypatch.setattr(
        "bitcaster.models.messagetemplate.MessageTemplate.render",
        Mock(side_effect=[Exception("boom"), ("s", "m", "h")]),
    )

    occurrence = Occurrence(event=notification.event, context={"foo": "bar"}, options={})
    success, data = occurrence.preview("full")

    assert success is True
    assert len(data["rendered"]) == 1  # second recipient still rendered
    assert data["rendered"][0]["assignment_pk"] == asm2.pk
    assert any("boom" in error for error in data["errors"])


def test_process_missing_template_does_not_crash(user: "User", monkeypatch: pytest.MonkeyPatch) -> None:
    from testutils.factories import AssignmentFactory, ChannelFactory, NotificationFactory

    from bitcaster.models import Occurrence

    notification: "Notification" = NotificationFactory.create(event__channels=[ChannelFactory()])
    assignment: "Assignment" = AssignmentFactory.create(channel=notification.event.channels.first())
    notification.distribution.recipients.add(assignment)
    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel",
        Mock(return_value=(None, None)),
    )
    monkeypatch.setattr("bitcaster.constants.bitcaster.trigger_event", Mock())

    occurrence: Occurrence = notification.event.trigger(context={})
    occurrence.process()

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSING
    assert occurrence.data["recipients"][0][5] is None  # template_pk None, no crash
    assert occurrence.data["messages"] == []
