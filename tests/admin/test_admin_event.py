from typing import TYPE_CHECKING, TypedDict

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Address, Application, Channel, Event

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "channel": Channel,
            "channel2": Channel,
            "event": Event,
            "address": Address,
            "address2": Address,
        },
    )


@pytest.fixture()
def app(django_app_factory, admin_user):
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context(django_app_factory, admin_user) -> "Context":
    from testutils.factories import AddressFactory, ChannelFactory, EventFactory

    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user

    channel = ChannelFactory()
    channel2 = ChannelFactory()
    event = EventFactory()
    event.channels.add(channel)
    event.channels.add(channel2)
    address = AddressFactory(user=admin_user)
    address2 = AddressFactory(user=admin_user)  # other_addr

    return {
        "app": django_app,
        "channel": channel,
        "channel2": channel2,
        "event": event,
        "address": address,
        "address2": address2,
    }
