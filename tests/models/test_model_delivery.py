# mypy: disable-error-code="attr-defined"
from typing import TYPE_CHECKING

import pytest
from testutils.factories import (
    AssignmentFactory,
    ChannelFactory,
    DeliveryFactory,
    MessageTemplateFactory,
    NotificationFactory,
)

from bitcaster.models import Delivery

if TYPE_CHECKING:
    from bitcaster.models import Assignment, Channel, Notification, Occurrence

pytestmark = pytest.mark.django_db


@pytest.fixture
def setup() -> "tuple[Occurrence, Assignment, Notification, Channel]":
    notification: Notification = NotificationFactory.create(event__channels=[ChannelFactory()])
    channel = notification.event.channels.first()
    asm: Assignment = AssignmentFactory(channel=channel)
    MessageTemplateFactory(channel=channel, event=notification.event, content="Hello {{ foo }}")
    notification.distribution.recipients.add(asm)
    occurrence: Occurrence = notification.event.trigger(context={"foo": "bar"})
    return occurrence, asm, notification, channel


def test_creation_defaults(setup: "tuple") -> None:
    occurrence, asm, notification, channel = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    assert delivery.status == Delivery.Status.PENDING
    assert delivery.errors == 0
    assert delivery.next_attempt_at is None
    assert delivery.occurrence == occurrence
    assert delivery.assignment == asm
    assert delivery.notification == notification
    assert delivery.channel == channel
    assert delivery.message_template is not None


def test_error_increment(setup: "tuple") -> None:
    occurrence, *_ = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    delivery.mark_error("boom")
    delivery.refresh_from_db()
    assert delivery.errors == 1
    assert delivery.status == Delivery.Status.ERROR
    assert delivery.next_attempt_at is not None
    assert delivery.data["errors"] == ["boom"]


def test_retry_scheduling(setup: "tuple") -> None:
    from freezegun import freeze_time

    occurrence, *_ = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    with freeze_time("2001-01-02T01:02:33Z"):
        delivery.mark_error("boom")
    delivery.refresh_from_db()
    assert delivery.next_attempt_at == delivery.next_attempt_at


def test_max_retries_sets_failure(setup: "tuple") -> None:
    from constance.test.pytest import override_config

    occurrence, *_ = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    with override_config(MAX_DELIVERY_RETRIES=3):
        for _ in range(3):
            delivery.mark_error("boom")
    delivery.refresh_from_db()
    assert delivery.status == Delivery.Status.FAILURE
    assert delivery.next_attempt_at is None


def test_error_below_max_keeps_retrying(setup: "tuple") -> None:
    from constance.test.pytest import override_config

    occurrence, *_ = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    with override_config(MAX_DELIVERY_RETRIES=3):
        delivery.mark_error("boom")
        delivery.mark_error("boom")
    delivery.refresh_from_db()
    assert delivery.status == Delivery.Status.ERROR
    assert delivery.next_attempt_at is not None


def test_send_success(setup: "tuple") -> None:
    occurrence, asm, _notification, _channel = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    result = delivery.send()
    assert result is True
    assert delivery.status == Delivery.Status.DELIVERED
    (message,) = delivery.channel.dispatcher._messages()
    assert message[1] == "Hello bar"


def test_send_failure_raises(setup: "tuple") -> None:
    from testutils.dispatcher import XDispatcher
    from unittest.mock import Mock, patch

    from bitcaster.exceptions import DispatcherError

    occurrence, *_ = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    with patch.object(XDispatcher, "_send", Mock(side_effect=DispatcherError("boom"))):
        with pytest.raises(DispatcherError):
            delivery.send()


def test_rendered_property(setup: "tuple") -> None:
    occurrence, *_ = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    assert delivery.rendered == {"subject": "", "message": "Hello bar", "html_message": ""}
    assert not delivery.missing_template


def test_uniqueness_constraint(setup: "tuple") -> None:
    from django.db import IntegrityError

    occurrence, asm, notification, channel = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    with pytest.raises(IntegrityError):
        Delivery.objects.create(
            occurrence=occurrence,
            assignment=asm,
            notification=notification,
            channel=channel,
        )


def test_str_and_natural_key(setup: "tuple") -> None:
    occurrence, *_ = setup
    occurrence.process()
    (delivery,) = occurrence.deliveries.all()
    assert str(delivery) == f"{occurrence} - {delivery.assignment}"
    assert delivery.natural_key() == (str(delivery.pk),) + occurrence.natural_key()


def test_factory_creation() -> None:
    delivery = DeliveryFactory()
    assert delivery.status == Delivery.Status.PENDING
    assert delivery.errors == 0
    assert delivery.next_attempt_at is None
