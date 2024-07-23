import os
from typing import TYPE_CHECKING, Any

import pytest
from strategy_field.utils import fqn

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import Payload

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_sys(mail_payload: "Payload", mailoutbox: list[Any]) -> None:
    from bitcaster.dispatchers import SystemDispatcher
    from bitcaster.models import Channel, Project

    SystemDispatcher(
        Channel(
            project=Project(from_email=os.environ["GMAIL_USER"], subject_prefix="[sys] "),
            dispatcher=fqn(SystemDispatcher),
        )
    ).send("test@example.com", mail_payload)
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == "[sys] subject"
