import os
from typing import TYPE_CHECKING, Any, Generator
from unittest.mock import Mock

import pytest
from constance.test.unittest import override_config
from django.core.exceptions import ValidationError
from django.urls import reverse
from strategy_field.utils import fqn
from testutils.helpers import assert_form_error

from bitcaster.dispatchers import UserMessageDispatcher
from bitcaster.models.choices import FILTERING_EXTERNAL

if TYPE_CHECKING:
    from responses import RequestsMock

    from bitcaster.dispatchers.base import Payload
    from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


@pytest.fixture
def system_channel(db: Any) -> "Generator[Channel, None, None]":
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    ch: Channel = ChannelFactory.create(
        dispatcher=fqn(GMailDispatcher),
        name="system-channel",
        config={"username": "username", "password": "password"},
    )
    with override_config(SYSTEM_EMAIL_CHANNEL=ch.pk):
        yield ch


@pytest.fixture
def data(system_channel):
    from testutils.factories import (
        ApplicationFactory,
        ChannelFactory,
        EventFactory,
        NotificationFactory,
    )

    app = ApplicationFactory.create()
    # working config
    n = NotificationFactory.create(
        event=EventFactory(channels=[system_channel], messages="abc"),
        policy=FILTERING_EXTERNAL,
    )

    return {
        "event0": EventFactory.create(application=app),
        "event1": EventFactory.create(channels=[ChannelFactory.create(project=app.project)]),
        "event2": EventFactory.create(
            channels=[ChannelFactory.create(project=app.project), ChannelFactory.create(project=app.project)]
        ),
        "event3": EventFactory.create(channels=[system_channel]),
        "event4": NotificationFactory.create(
            event__channels=[system_channel],
            policy=FILTERING_EXTERNAL,
        ).event,
        "event_ok": n.event,
    }


@pytest.mark.parametrize("mail_payload", ["", "html_message"], indirect=True)
def test_usermessage(
    mocked_responses: "RequestsMock", monkeypatch: pytest.MonkeyPatch, mail_payload: "Payload"
) -> None:
    from bitcaster.models import Channel, Project

    ch = Channel(
        project=Project(from_email=os.environ["GMAIL_USER"], subject_prefix="[gmail] "),
        config={},
    )
    UserMessageDispatcher(ch).send("test@example.com", mail_payload, Mock())


def test_config() -> None:
    d: UserMessageDispatcher = UserMessageDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        _ = d.config


def test_create(django_app, admin_user, project, data) -> None:
    event0 = data["event0"]
    event1 = data["event1"]
    event2 = data["event2"]
    event3 = data["event3"]
    event4 = data["event4"]
    event_ok = data["event_ok"]

    url = reverse("admin:bitcaster_channel_add")
    res = django_app.get(url, user=admin_user)
    frm = res.forms["channel_form"]
    frm["organization"].force_value(project.organization.pk)
    frm["project"].force_value(project.pk)
    frm["name"] = "Channel-1"
    frm["dispatcher"] = fqn(UserMessageDispatcher)
    res = frm.submit("_continue").follow()
    res = res.click("Configure")
    res = res.forms["config-form"].submit()
    assert_form_error(res, "event", "This field is required.")

    res.forms["config-form"]["event"] = event0.pk
    res = res.forms["config-form"].submit()
    assert_form_error(res, "event", "Event does not have any Channel configured")

    res.forms["config-form"]["event"] = event2.pk
    res = res.forms["config-form"].submit()
    assert_form_error(res, "event", "Event must have only one Channel configured")

    res.forms["config-form"]["event"] = event1.pk
    res = res.forms["config-form"].submit()
    assert_form_error(res, "event", "Event must use system Email Channel")

    res.forms["config-form"]["event"] = event3.pk
    res = res.forms["config-form"].submit()
    assert_form_error(res, "event", "At least one notification with external_filtering=True must be configured")

    res.forms["config-form"]["event"] = event4.pk
    res = res.forms["config-form"].submit()
    assert_form_error(res, "event", "Event does not have any Message Template configured")

    res.forms["config-form"]["event"] = event_ok.pk
    res = res.forms["config-form"].submit().follow()
    res.click("Configure")
