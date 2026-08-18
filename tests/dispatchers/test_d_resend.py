import pytest
from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from strategy_field.utils import fqn

from bitcaster.dispatchers import ResendDispatcher
from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_resend_send(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    with patch("anymail.backends.resend.EmailBackend.send_messages") as mock_send:
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[resend] "),
            dispatcher=fqn(ResendDispatcher),
            config={"api_key": "test-api-key"},
        )
        result = ResendDispatcher(ch).send("recipient@example.com", mail_payload)
        assert result is True
        mock_send.assert_called_once()


def test_resend_error(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    with patch("anymail.backends.resend.EmailBackend.send_messages", side_effect=Exception("API Error")):
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[resend] "),
            dispatcher=fqn(ResendDispatcher),
            config={"api_key": "invalid-key"},
        )
        with pytest.raises(DispatcherError):
            ResendDispatcher(ch).send("recipient@example.com", mail_payload)


def test_config_empty() -> None:
    d = ResendDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        _ = d.config
