import pytest
from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from strategy_field.utils import fqn

from bitcaster.dispatchers import SendGridDispatcher
from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_sendgrid_send(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    with patch("anymail.backends.sendgrid.EmailBackend.send_messages") as mock_send:
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[sendgrid] "),
            dispatcher=fqn(SendGridDispatcher),
            config={"api_key": "test-api-key"},
        )
        result = SendGridDispatcher(ch).send("recipient@example.com", mail_payload)
        assert result is True
        mock_send.assert_called_once()


def test_sendgrid_with_custom_from(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    with patch("anymail.backends.sendgrid.EmailBackend.send_messages"):
        ch = Channel(
            project=Project(from_email="project@example.com", subject_prefix="[sendgrid] "),
            dispatcher=fqn(SendGridDispatcher),
            config={
                "api_key": "test-api-key",
                "from_address": "custom@example.com",
                "from_label": "Custom Label",
            },
        )
        result = SendGridDispatcher(ch).send("recipient@example.com", mail_payload)
        assert result is True


def test_sendgrid_error(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    with patch("anymail.backends.sendgrid.EmailBackend.send_messages", side_effect=Exception("API Error")):
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[sendgrid] "),
            dispatcher=fqn(SendGridDispatcher),
            config={"api_key": "invalid-key"},
        )
        with pytest.raises(DispatcherError):
            SendGridDispatcher(ch).send("recipient@example.com", mail_payload)


def test_config_empty() -> None:
    d = SendGridDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        _ = d.config
