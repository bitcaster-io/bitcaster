import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers import SlackDispatcher
from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_twilio_send(mail_payload, mocked_responses, twilio_sid):
    mocked_responses.add(mocked_responses.POST, "http://test-slack.com/abdce/", json={"ok": True})
    ch = Channel(
        dispatcher=fqn(SlackDispatcher),
        config={"url": "http://test-slack.com/abdce/"},
    )

    assert SlackDispatcher(ch).send("123456", mail_payload)
