from unittest import mock

import pytest

from bitcaster.agents import GMailAgent
from bitcaster.agents.handlers.mail import ImapMessage

pytestmark = pytest.mark.django_db


# GmailMessage

def test_emailmessage():
    msg = ImapMessage(b'')
    with mock.patch.object(msg, 'email_message'):
        assert msg.subject
        assert msg.sender
        assert msg.recipient


def test_agent_get_usage(monitor1):
    agent = GMailAgent(monitor1)
    assert agent.get_usage()
