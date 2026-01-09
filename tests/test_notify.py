from typing import TYPE_CHECKING, TypedDict

import pytest
from strategy_field.utils import fqn
from testutils.dispatcher import XDispatcher

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
        MessageFactory,
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

    NotificationFactory.create(event=evt, distribution=dis)
    msg = MessageFactory.create(
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
    }


def test_trigger(context: "Context", django_assert_num_queries: "DjangoAssertNumQueries") -> None:
    event: Event = context["event"]
    v1: Assignment = context["v1"]
    v2: Assignment = context["v2"]
    ch: Channel = context["channel"]
    o = event.trigger(context={})
    assert event.notifications.exists()
    o.process()

    assert sorted(ch.dispatcher._messages()) == sorted(
        [
            [v1.address.value, f"Message for {event.name} on channel {ch.name}", 0],
            [v2.address.value, f"Message for {event.name} on channel {ch.name}", 1],
        ]
    )
    o.refresh_from_db()
    assert o.data == {
        "delivered": [v1.pk, v2.pk],
        "recipients": [
            [v1.address.value, v1.channel.name],
            [v2.address.value, v2.channel.name],
        ],
        "errors": [],
    }
