import pytest
from responses import RequestsMock
from strategy_field.utils import fqn

from bitcaster.dispatchers import SlackDispatcher
from bitcaster.dispatchers.base import Payload
from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_twilio_send(mail_payload: Payload, mocked_responses: RequestsMock, twilio_sid: str) -> None:
    mocked_responses.add(mocked_responses.POST, "http://test-slack.com/abdce/", json={"ok": True})
    ch = Channel(
        dispatcher=fqn(SlackDispatcher),
        config={"url": "http://test-slack.com/abdce/"},
    )

    assert SlackDispatcher(ch).send("123456", mail_payload)
