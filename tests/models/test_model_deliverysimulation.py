from typing import TYPE_CHECKING

import pytest
from testutils.factories import (
    AssignmentFactory,
    ChannelFactory,
    EventSimulationFactory,
    MessageTemplateFactory,
    NotificationFactory,
)

from bitcaster.models import DeliverySimulation, MessageTemplate, Notification, Occurrence

if TYPE_CHECKING:
    from bitcaster.models import Assignment, Channel, EventSimulation

pytestmark = pytest.mark.django_db


@pytest.fixture
def simulation() -> "tuple[EventSimulation, dict, Assignment, Notification, Channel]":
    notification: Notification = NotificationFactory.create(event__channels=[ChannelFactory()])
    channel = notification.event.channels.first()
    asm: Assignment = AssignmentFactory(channel=channel)
    MessageTemplateFactory(channel=channel, event=notification.event, content="Hello {{ foo }}")
    notification.distribution.recipients.add(asm)
    sim: EventSimulation = EventSimulationFactory(event=notification.event, mode="full")
    success, data = Occurrence(event=notification.event, context={"foo": "bar"}, options={}).preview("full")
    assert success
    return sim, data, asm, notification, channel


def test_save_deliveries_full(simulation: "tuple") -> None:
    sim, data, asm, notification, _channel = simulation
    sim.save_deliveries(data)

    sim.refresh_from_db()
    assert sim.status == Occurrence.Status.PROCESSED.value
    assert sim.data["recipients_count"] == 1
    assert sim.data["rendered_count"] == 1
    assert sim.data["notifications"] == [notification.pk]
    assert len(sim.data["channels"]) == 1

    deliveries = list(sim.deliveries.all())
    assert len(deliveries) == 1
    (delivery,) = deliveries
    assert delivery.assignment == asm
    assert delivery.notification == notification
    assert delivery.message_template is not None
    assert delivery.rendered == {"subject": "", "message": "Hello bar", "html_message": ""}
    assert delivery.status == Occurrence.Status.PROCESSED.value
    assert not delivery.missing_template


def test_save_deliveries_missing_template(simulation: "tuple") -> None:
    sim, _data, _asm, _notification, _channel = simulation
    MessageTemplate.objects.all().delete()

    _, data = Occurrence(event=sim.event, context={"foo": "bar"}, options={}).preview("full")
    sim.save_deliveries(data)

    sim.refresh_from_db()
    assert sim.data["missing_template_count"] == 1
    (delivery,) = sim.deliveries.all()
    assert delivery.message_template is None
    assert delivery.missing_template
    assert delivery.rendered is None


def test_save_deliveries_multiple_notifications(simulation: "tuple") -> None:
    sim, _data, asm, _notification, _channel = simulation
    for _ in range(2):
        NotificationFactory(event=sim.event, distribution__recipients=[asm])
    _, data = Occurrence(event=sim.event, context={"foo": "bar"}, options={}).preview("full")

    sim.save_deliveries(data)

    sim.refresh_from_db()
    assert sim.deliveries.count() == 3
    assert sim.data["recipients_count"] == 3
    assert len({d.notification_id for d in sim.deliveries.all()}) == 3


def test_save_deliveries_strips_per_recipient_data(simulation: "tuple") -> None:
    sim, data, *_ = simulation
    sim.save_deliveries(data)
    sim.refresh_from_db()
    assert "recipients" not in sim.data
    assert "rendered" not in sim.data
    assert "missing_template" not in sim.data


def test_save_deliveries_idempotent(simulation: "tuple") -> None:
    sim, data, *_ = simulation
    sim.save_deliveries(data)
    sim.save_deliveries(data)
    assert sim.deliveries.count() == 1


def test_save_deliveries_does_not_overwrite_processed() -> None:
    sim = EventSimulationFactory(status=Occurrence.Status.PROCESSED.value, data={"errors": ["previous"]})
    sim.save_deliveries({"delivered": [], "recipients": []})
    sim.refresh_from_db()
    assert sim.status == Occurrence.Status.PROCESSED.value
    assert sim.data == {"errors": ["previous"]}
    assert sim.deliveries.count() == 0


def test_save_deliveries_cascade_on_delete(simulation: "tuple") -> None:
    sim, data, *_ = simulation
    sim.save_deliveries(data)
    assert sim.deliveries.count() == 1

    sim.delete()
    assert DeliverySimulation.objects.count() == 0


def test_deliveries_stores_errors(simulation: "tuple") -> None:
    sim, data, *_ = simulation
    data["errors"] = ["template boom"]
    sim.save_deliveries(data)
    sim.refresh_from_db()
    assert sim.data["errors"] == ["template boom"]


def test_delivery_str_and_natural_key(simulation: "tuple") -> None:
    sim, data, *_ = simulation
    sim.save_deliveries(data)
    (delivery,) = sim.deliveries.all()
    assert str(delivery) == f"{sim} - {delivery.assignment}"
    assert delivery.natural_key() == (str(delivery.pk),) + sim.natural_key()


def test_status_choices_match_occurrence() -> None:
    field = DeliverySimulation._meta.get_field("status")
    assert dict(field.choices) == dict(Occurrence.Status.choices)


def test_event_simulation_choices_and_natural_key() -> None:
    from testutils.factories import EventSimulationFactory

    from bitcaster.models import EventSimulation

    sim = EventSimulationFactory()
    field = EventSimulation._meta.get_field("status")
    assert dict(field.choices) == dict(Occurrence.Status.choices)
    assert sim.natural_key() == (str(sim.pk),) + sim.event.natural_key()
