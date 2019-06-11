from unittest import mock

import pytest

from bitcaster.agents.handlers.imap import ImapAgent, ImapMessage

pytestmark = pytest.mark.django_db


# EmailMessage

def test_emailmessage():
    msg = ImapMessage(b'')
    with mock.patch.object(msg, 'email_message'):
        assert msg.subject
        assert msg.sender
        assert msg.recipient


def test_agent_get_usage(monitor1):
    agent = ImapAgent(monitor1)
    assert agent.get_usage()


def test_agent_fqn(monitor1):
    agent = ImapAgent(monitor1)
    assert agent.fqn
