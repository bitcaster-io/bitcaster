from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from strategy_field.utils import fqn

from bitcaster.forms.locking import LockingModeChoice
from bitcaster.models import Channel
from bitcaster.state import state

if TYPE_CHECKING:

    Context = TypedDict(
        "Context",
        {
            "channel": Channel,
            "other_channel": Channel,
            "locked_channel": Channel,
        },
    )


@pytest.fixture()
def app(django_app_factory, rf, db):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request = rf.get("/")
    request.user = admin_user
    with state.configure(request=request):
        yield django_app


@pytest.fixture
def context(django_app_factory, admin_user) -> "Context":
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    gmail_channel = ChannelFactory(
        dispatcher=fqn(GMailDispatcher), config={"username": "username", "password": "password"}
    )
    locked_channel = ChannelFactory(
        organization=gmail_channel.organization,
        locked=True,
        dispatcher=fqn(GMailDispatcher),
        config={"username": "username", "password": "password"},
    )
    other_channel = ChannelFactory(
        dispatcher=fqn(GMailDispatcher), config={"username": "username", "password": "password"}
    )

    return {"channel": gmail_channel, "other_channel": other_channel, "locked_channel": locked_channel}


def test_bychannel(app: DjangoTestApp, context):
    url = reverse("locking")
    res = app.get(url)
    assert res.status_code == 200

    res.form["mode-operation"] = LockingModeChoice.CHANNEL
    res = res.form.submit()

    assert res.form["channel-channel"].options == [
        (str(context["channel"].id), False, context["channel"].name),
        (str(context["other_channel"].id), False, context["other_channel"].name),
    ]

    res.form["channel-channel"].select_multiple([str(context["channel"].id), str(context["other_channel"].id)])
    res = res.form.submit()

    res = app.post(url, {"username": "", "password": ""})
    assert res.status_code == 200

    res = app.post(url, {"username": "username", "password": "password"})
    assert res.status_code == 302
