from typing import TYPE_CHECKING, TypedDict

from strategy_field.utils import fqn

from bitcaster.dispatchers.test import TestDispatcher

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application, Channel, EventType, Subscription, User, Address

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "event": EventType,
            "key": ApiKey,
            "channel": Channel,
            "subscription": Subscription,
        },
    )


def test_event(db):
    from testutils.factories import (
        ApiKeyFactory,
        ApplicationFactory,
        ChannelFactory,
        EventTypeFactory,
        SubscriptionFactory,
        UserFactory,
        AddressFactory,
    )
    user: "User" = UserFactory()
    addr: "Address" = AddressFactory(user=user)
    app = ApplicationFactory(name="Application-000")
    evt: EventType = EventTypeFactory(application=app)
    ch = ChannelFactory(organization=app.project.organization, name="test", dispatcher=fqn(TestDispatcher))

    key = ApiKeyFactory(application=app)
    user: "User" = key.user

    sub = SubscriptionFactory(user=user, channels=[ch], event=evt)

    context = {"app": app, "event": evt, "key": key, "channel": ch, "subscription": sub}
    evt.trigger(context)
