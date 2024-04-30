from typing import TYPE_CHECKING, TypedDict

import pytest
from pytest_django import DjangoAssertNumQueries
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

if TYPE_CHECKING:
    from bitcaster.models import (
        Address,
        ApiKey,
        Application,
        Channel,
        DistributionList,
        Event,
        Message,
        User,
        Validation,
    )

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "event": Event,
            "key": ApiKey,
            "channel": Channel,
            "v1": Validation,
            "v2": Validation,
            "message": Message,
            "address": Address,
        },
    )


@pytest.fixture
def context(db) -> "Context":
    from testutils.factories import (
        AddressFactory,
        ApiKeyFactory,
        ApplicationFactory,
        ChannelFactory,
        DistributionListFactory,
        EventFactory,
        MessageFactory,
        NotificationFactory,
        ValidationFactory,
    )

    app: "Application" = ApplicationFactory(name="Application-000")

    key: "ApiKey" = ApiKeyFactory(application=app)
    user: "User" = key.user
    addr: Address = AddressFactory(value="addr1@example.com", user=user)

    ch = ChannelFactory(organization=app.project.organization, name="test", dispatcher=fqn(TDispatcher))
    evt = EventFactory(application=app, channels=[ch])
    dis: "DistributionList" = DistributionListFactory()
    v1: Validation = ValidationFactory(address=addr, channel=ch)
    v2: Validation = ValidationFactory(address__value="addr2@example.com", channel=ch)

    NotificationFactory(event=evt, distribution=dis)
    msg = MessageFactory(channel=ch, event=evt, content="Message for {{ event.name }} on channel {{channel.name}}")

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


def test_trigger(context: "Context", messagebox, django_assert_num_queries: "DjangoAssertNumQueries"):
    event: Event = context["event"]
    v1: Validation = context["v1"]
    v2: Validation = context["v2"]
    ch: Channel = context["channel"]
    o = event.trigger({})
    assert event.notifications.exists()
    # with django_assert_num_queries(10) as captured:
    o.process()
    # msgs_queries = [q for q in captured if q["sql"].startswith('SELECT "bitcaster_message"')]
    # assert len(msgs_queries) == 1, "get_message() cache is not working"

    assert messagebox == [
        (v1.address.value, f"Message for {event.name} on channel {ch.name}"),
        (v2.address.value, f"Message for {event.name} on channel {ch.name}"),
    ]
    o.refresh_from_db()
    assert o.status == {
        "delivered": [v1.pk, v2.pk],
        "recipients": [
            [v1.address.value, v1.channel.name],
            [v2.address.value, v2.channel.name],
        ],
    }
