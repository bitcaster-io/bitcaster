from typing import TYPE_CHECKING, TypedDict

import pytest
from testutils.dispatcher import XDispatcher
from unittest.mock import ANY

from strategy_field.utils import fqn

if TYPE_CHECKING:
    from pytest_django import DjangoAssertNumQueries

    from bitcaster.models import (
        Address,
        ApiKey,
        Application,
        Assignment,
        Channel,
        DistributionList,
        Event,
        MessageTemplate,
        Notification,
        User,
    )

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "event": Event,
            "key": ApiKey,
            "channel": Channel,
            "v1": Assignment,
            "v2": Assignment,
            "message": MessageTemplate,
            "address": Address,
            "notification": Notification,
        },
    )

pytestmark = pytest.mark.django_db


@pytest.fixture
def context() -> "Context":
    from testutils.factories import (
        AddressFactory,
        ApiKeyFactory,
        ApplicationFactory,
        AssignmentFactory,
        ChannelFactory,
        DistributionListFactory,
        EventFactory,
        MessageTemplateFactory,
        NotificationFactory,
    )

    app: "Application" = ApplicationFactory.create(name="Application-000")

    key: "ApiKey" = ApiKeyFactory.create(application=app)
    user: "User" = key.user
    addr: Address = AddressFactory.create(value="addr1@example.com", user=user)

    ch = ChannelFactory.create(organization=app.project.organization, name="test", dispatcher=fqn(XDispatcher))
    evt = EventFactory.create(application=app, channels=[ch])
    dis: "DistributionList" = DistributionListFactory.create()
    v1: Assignment = AssignmentFactory.create(address=addr, channel=ch)
    v2: Assignment = AssignmentFactory.create(address__value="addr2@example.com", channel=ch)

    n = NotificationFactory.create(event=evt, distribution=dis)
    msg = MessageTemplateFactory.create(
        channel=ch, event=evt, content="Message for {{ event.name }} on channel {{channel.name}}"
    )

    dis.recipients.add(v1)
    dis.recipients.add(v2)

    return {
        "app": app,
        "event": evt,
        "key": key,
        "channel": ch,
        "v1": v1,
        "v2": v2,
        "message": msg,
        "address": addr,
        "notification": n,
    }


def test_trigger(context: "Context", django_assert_num_queries: "DjangoAssertNumQueries") -> None:
    event: Event = context["event"]
    v1: Assignment = context["v1"]
    v2: Assignment = context["v2"]
    ch: Channel = context["channel"]
    msg: MessageTemplate = context["message"]
    n: Notification = context["notification"]
    o = event.trigger(context={})
    assert event.notifications.exists()
    o.process()

    assert ch.dispatcher._messages() == []
    o.refresh_from_db()
    assert o.recipients == 2
    assert o.deliveries.count() == 2
    assert o.data == {
        "delivered": [],
        "recipients": [
            [v1.address.value, v1.channel.name, v1.pk, ch.pk, n.pk, msg.pk],
            [v2.address.value, v2.channel.name, v2.pk, ch.pk, n.pk, msg.pk],
        ],
        "errors": [],
        "messages": [msg.pk],
        "notifications": [n.pk],
        "channels": [ch.pk],
        "rendered": [
            {
                "assignment_pk": v1.pk,
                "notification_pk": n.pk,
                "notification_name": n.name,
                "channel_pk": ch.pk,
                "channel_name": ch.name,
                "address": v1.address.value,
                "subject": "",
                "message": f"Message for {event.name} on channel {ch.name}",
                "html_message": "",
            },
            {
                "assignment_pk": v2.pk,
                "notification_pk": n.pk,
                "notification_name": n.name,
                "channel_pk": ch.pk,
                "channel_name": ch.name,
                "address": v2.address.value,
                "subject": "",
                "message": f"Message for {event.name} on channel {ch.name}",
                "html_message": "",
            },
        ],
        "missing_template": [],
        "phase1_at": "",
        "phase2_attempts": [],
        "processing": {
            "phase1_at": ANY,
            "phase2_attempts": [],
        },
    }
