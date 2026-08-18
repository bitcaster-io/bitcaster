import pytest
from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from strategy_field.utils import fqn

from bitcaster.dispatchers import PostmarkDispatcher
from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_postmark_send(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    with patch("anymail.backends.postmark.EmailBackend.send_messages") as mock_send:
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[postmark] "),
            dispatcher=fqn(PostmarkDispatcher),
            config={"server_token": "test-server-token"},
        )
        result = PostmarkDispatcher(ch).send("recipient@example.com", mail_payload)
        assert result is True
        mock_send.assert_called_once()


def test_postmark_error(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    with patch("anymail.backends.postmark.EmailBackend.send_messages", side_effect=Exception("API Error")):
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[postmark] "),
            dispatcher=fqn(PostmarkDispatcher),
            config={"server_token": "invalid-token"},
        )
        with pytest.raises(DispatcherError):
            PostmarkDispatcher(ch).send("recipient@example.com", mail_payload)


def test_config_empty() -> None:
    d = PostmarkDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        _ = d.config
