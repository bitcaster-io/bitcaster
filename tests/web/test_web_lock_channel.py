from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from strategy_field.utils import fqn

from bitcaster.constants import Bitcaster
from bitcaster.forms.locking import LockingModeChoice
from bitcaster.state import state

if TYPE_CHECKING:
    from bitcaster.models import Channel

    Context = TypedDict(
        "Context",
        {"channel": Channel, "other_channel": Channel, "locked_channel": Channel, "bitcaster_channel": Channel},
    )


@pytest.fixture
def context(django_app_factory, admin_user) -> "Context":
    from testutils.factories.channel import ChannelFactory, OrganizationFactory

    from bitcaster.dispatchers import GMailDispatcher

    bitcaster_org = OrganizationFactory(name=Bitcaster.ORGANIZATION)

    gmail_channel = ChannelFactory(
        dispatcher=fqn(GMailDispatcher), config={"username": "username", "password": "password"}
    )
    locked_channel = ChannelFactory(
        organization=gmail_channel.organization,
        project=gmail_channel.project,
        locked=True,
        dispatcher=fqn(GMailDispatcher),
        config={"username": "username", "password": "password"},
    )
    other_channel = ChannelFactory(
        dispatcher=fqn(GMailDispatcher), config={"username": "username", "password": "password"}, project=None
    )
    bitcaster_channel = ChannelFactory(
        organization=bitcaster_org,
        dispatcher=fqn(GMailDispatcher),
        config={"username": "username", "password": "password"},
        project=None,
    )

    return {
        "channel": gmail_channel,
        "other_channel": other_channel,
        "locked_channel": locked_channel,
        "bitcaster_channel": bitcaster_channel,
    }


def test_bychannel(app: DjangoTestApp, context):
    from bitcaster.models import Channel

    url = reverse("locking")
    res = app.get(url)
    assert res.status_code == 200

    channels = set(Channel.objects.filter(locked=True).values_list("id", flat=True))
    assert channels == {context["locked_channel"].id}

    res.form["mode-operation"] = LockingModeChoice.CHANNEL
    res = res.form.submit()

    assert res.form["channel-channel"].options == [
        (str(context["channel"].id), False, context["channel"].name),
        (str(context["other_channel"].id), False, context["other_channel"].name),
    ]

    res.form["channel-channel"].select_multiple([str(context["channel"].id), str(context["other_channel"].id)])
    res = res.form.submit()
    assert res.status_code == 200

    channels = set(Channel.objects.filter(locked=True).values_list("id", flat=True))
    assert channels == {context["locked_channel"].id, context["channel"].id, context["other_channel"].id}

    assert "The following channels have been locked" in res.text
    assert context["locked_channel"].name not in res.text
    assert context["other_channel"].name in res.text
    assert context["channel"].name in res.text
