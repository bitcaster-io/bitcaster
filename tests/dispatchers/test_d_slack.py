from responses import RequestsMock

import pytest

from strategy_field.utils import fqn

from bitcaster.dispatchers import SlackDispatcher
from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError
from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_slack_send(mail_payload: Payload, mocked_responses: RequestsMock, twilio_sid: str) -> None:
    mocked_responses.add(mocked_responses.POST, "https://hooks.slack.com/abdce/", json={"ok": True})
    ch = Channel(
        dispatcher=fqn(SlackDispatcher),
        config={"url": "https://hooks.slack.com/abdce/"},
    )

    assert SlackDispatcher(ch).send("123456", mail_payload)


def test_slack_send_invalid_url(mail_payload: Payload) -> None:
    ch = Channel(
        dispatcher=fqn(SlackDispatcher),
        config={"url": "https://test-slack.com/abdce/"},
    )

    with pytest.raises(DispatcherError) as excinfo:
        SlackDispatcher(ch).send("123456", mail_payload)
    assert "URL must be a valid Slack webhook" in str(excinfo.value)
