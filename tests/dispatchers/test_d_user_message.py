import os
from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from strategy_field.utils import fqn

from bitcaster.dispatchers import UserMessageDispatcher

if TYPE_CHECKING:
    from responses import RequestsMock

    from bitcaster.dispatchers.base import Payload

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


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


def test_create(django_app, admin_user, project) -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = django_app.get(url, user=admin_user)
    frm = res.forms["channel_form"]
    frm["organization"].force_value(project.organization.pk)
    frm["project"].force_value(project.pk)
    frm["name"] = "Channel-1"
    frm["dispatcher"] = fqn(UserMessageDispatcher)
    res = frm.submit("_continue").follow()
    res = res.click("Configure")
