import json

import pytest
from unittest.mock import MagicMock, patch

from strategy_field.utils import fqn

from bitcaster.dispatchers import RabbitMQDispatcher
from bitcaster.dispatchers.base import Payload
from bitcaster.exceptions import DispatcherError
from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_rabbitmq_send(mail_payload: Payload) -> None:
    ch = Channel(
        dispatcher=fqn(RabbitMQDispatcher),
        config={
            "host": "localhost",
            "port": 5672,
            "username": "guest",
            "password": "guest",
            "vhost": "/",
            "exchange": "test-exchange",
            "exchange_type": "topic",
            "routing_key": "test.key",
        },
    )

    with patch("bitcaster.dispatchers.rabbitmq.pika.BlockingConnection") as mock_conn:
        mock_channel = MagicMock()
        mock_conn.return_value.channel.return_value = mock_channel

        result = RabbitMQDispatcher(ch).send("addr", mail_payload)

        assert result is True
        mock_conn.assert_called_once()
        mock_channel.exchange_declare.assert_called_once_with(
            exchange="test-exchange",
            exchange_type="topic",
            durable=True,
        )
        mock_channel.basic_publish.assert_called_once()
        call_kwargs = mock_channel.basic_publish.call_args[1]
        assert call_kwargs["exchange"] == "test-exchange"
        assert call_kwargs["routing_key"] == "test.key"


def test_rabbitmq_default_routing_key(mail_payload: Payload) -> None:
    ch = Channel(
        dispatcher=fqn(RabbitMQDispatcher),
        config={
            "host": "localhost",
            "port": 5672,
            "exchange": "test-exchange",
            "exchange_type": "topic",
        },
    )

    with patch("bitcaster.dispatchers.rabbitmq.pika.BlockingConnection") as mock_conn:
        mock_channel = MagicMock()
        mock_conn.return_value.channel.return_value = mock_channel

        RabbitMQDispatcher(ch).send("addr", mail_payload)

        call_kwargs = mock_channel.basic_publish.call_args[1]
        assert call_kwargs["routing_key"] == mail_payload.event.slug


def test_rabbitmq_send_failure(mail_payload: Payload) -> None:
    ch = Channel(
        dispatcher=fqn(RabbitMQDispatcher),
        config={
            "host": "localhost",
            "port": 5672,
            "exchange": "test-exchange",
            "exchange_type": "topic",
        },
    )

    with patch("bitcaster.dispatchers.rabbitmq.pika.BlockingConnection") as mock_conn:
        mock_conn.side_effect = Exception("Connection refused")

        with pytest.raises(DispatcherError, match="RabbitMQ publish failed"):
            RabbitMQDispatcher(ch).send("addr", mail_payload)


def test_rabbitmq_payload_json(mail_payload: Payload) -> None:
    ch = Channel(
        dispatcher=fqn(RabbitMQDispatcher),
        config={
            "host": "localhost",
            "port": 5672,
            "exchange": "test-exchange",
            "exchange_type": "topic",
        },
    )

    with patch("bitcaster.dispatchers.rabbitmq.pika.BlockingConnection") as mock_conn:
        mock_channel = MagicMock()
        mock_conn.return_value.channel.return_value = mock_channel

        RabbitMQDispatcher(ch).send("addr", mail_payload)

        call_kwargs = mock_channel.basic_publish.call_args[1]
        body = json.loads(call_kwargs["body"])
        assert body["message"] == "message"
        assert body["subject"] == "subject"
        assert body["event"] == mail_payload.event.slug
