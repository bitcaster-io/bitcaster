import pytest
from unittest.mock import Mock, patch

from django.core.exceptions import ValidationError
from strategy_field.utils import fqn

from bitcaster.dispatchers import AmazonSESDispatcher
from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def _mock_ses_client() -> Mock:
    client = Mock()
    client.send_email.return_value = {"MessageId": "test-message-id"}
    return client


def test_ses_send(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    client = _mock_ses_client()
    with patch("anymail.backends.amazon_ses.boto3.session.Session") as mock_session:
        mock_session.return_value.client.return_value = client
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[ses] "),
            dispatcher=fqn(AmazonSESDispatcher),
            config={
                "aws_access_key_id": "test-access-key",
                "aws_secret_access_key": "test-secret-key",
                "aws_region": "eu-west-1",
            },
        )
        result = AmazonSESDispatcher(ch).send("recipient@example.com", mail_payload)
        assert result is True
        client.send_email.assert_called_once()


def test_ses_send_default_region(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    client = _mock_ses_client()
    with patch("anymail.backends.amazon_ses.boto3.session.Session") as mock_session:
        mock_session.return_value.client.return_value = client
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[ses] "),
            dispatcher=fqn(AmazonSESDispatcher),
            config={
                "aws_access_key_id": "test-access-key",
                "aws_secret_access_key": "test-secret-key",
            },
        )
        result = AmazonSESDispatcher(ch).send("recipient@example.com", mail_payload)
        assert result is True
        client.send_email.assert_called_once()


def test_ses_error(mail_payload: Payload) -> None:
    from bitcaster.models import Channel, Project

    client = _mock_ses_client()
    client.send_email.side_effect = Exception("API Error")
    with patch("anymail.backends.amazon_ses.boto3.session.Session") as mock_session:
        mock_session.return_value.client.return_value = client
        ch = Channel(
            project=Project(from_email="sender@example.com", subject_prefix="[ses] "),
            dispatcher=fqn(AmazonSESDispatcher),
            config={
                "aws_access_key_id": "test-access-key",
                "aws_secret_access_key": "test-secret-key",
            },
        )
        with pytest.raises(DispatcherError):
            AmazonSESDispatcher(ch).send("recipient@example.com", mail_payload)


def test_config_empty() -> None:
    d = AmazonSESDispatcher(Mock(config={}))
    with pytest.raises(ValidationError):
        _ = d.config
