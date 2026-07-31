import json

import pika

import pytest
from unittest.mock import MagicMock, patch

from bitcaster.agents.amqp import AgentAMQP
from bitcaster.models import Event, Monitor


@pytest.fixture
def monitor(event: "Event") -> MagicMock:
    mon = MagicMock(spec=Monitor)
    mon.event = event
    mon.config = {
        "host": "rabbitmq.example.com",
        "port": 5672,
        "virtual_host": "/",
        "username": "user",
        "password": "pass",
        "queue": "test_queue",
        "exchange": "test_exchange",
        "routing_key": "test.key",
        "prefetch_count": 1,
        "event_field": "event",
        "max_messages": 10,
    }
    return mon


@pytest.fixture
def agent(monitor: MagicMock) -> AgentAMQP:
    return AgentAMQP(monitor)


def make_message(event_slug: str, data: dict | None = None) -> bytes:
    return json.dumps({"event": event_slug, "data": data or {"key": "value"}}).encode()


def make_channel_mock(messages: list[bytes] | None = None) -> MagicMock:
    channel = MagicMock()
    if messages:
        frames = []
        for i, body in enumerate(messages):
            method = MagicMock()
            method.delivery_tag = i + 1
            frames.append((method, MagicMock(), body))
        channel.consume.return_value = frames
    else:
        channel.consume.return_value = [(None, None, None)]
    return channel


class TestAMQPConfig:
    def test_config_valid(self) -> None:
        from bitcaster.agents.amqp import AMQPConfig

        cfg = AMQPConfig(
            data={
                "host": "localhost",
                "port": 5672,
                "username": "user",
                "password": "pass",
                "queue": "q",
            }
        )
        assert cfg.is_valid()

    def test_config_defaults(self) -> None:
        from bitcaster.agents.amqp import AMQPConfig

        cfg = AMQPConfig(
            data={
                "host": "localhost",
                "port": 5672,
                "username": "user",
                "password": "pass",
                "queue": "q",
            }
        )
        assert cfg.is_valid()

    def test_config_missing_required(self) -> None:
        from bitcaster.agents.amqp import AMQPConfig

        cfg = AMQPConfig(data={})
        assert not cfg.is_valid()
        assert "host" in cfg.errors
        assert "username" in cfg.errors
        assert "password" in cfg.errors
        assert "queue" in cfg.errors


class TestAgentAMQP:
    def test_verbose_name(self) -> None:
        assert AgentAMQP.verbose_name == "RabbitMQ"

    def test_cfg_defaults(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        monitor.config = {"host": "h", "port": 5672, "username": "u", "password": "p", "queue": "q"}
        c = agent.cfg
        assert c["port"] == 5672
        assert c["virtual_host"] == "/"
        assert c["exchange"] == ""
        assert c["prefetch_count"] == 1
        assert c["event_field"] == "event"
        assert c["max_messages"] == 10

    def test_changes_detected_true(self, agent: AgentAMQP) -> None:
        channel = MagicMock()
        method = MagicMock()
        method.delivery_tag = 1
        channel.basic_get.return_value = (method, MagicMock(), b"{}")
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            assert agent.changes_detected() is True
            channel.basic_nack.assert_called_once_with(1, requeue=True)

    def test_changes_detected_false(self, agent: AgentAMQP) -> None:
        channel = MagicMock()
        channel.basic_get.return_value = (None, None, None)
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            assert agent.changes_detected() is False

    def test_check_consumes_and_triggers(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        body = make_message(monitor.event.slug, {"order_id": "123"})
        channel = make_channel_mock([body])
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            with patch.object(Event, "trigger") as trigger:
                agent.check()
                trigger.assert_called_once()
                assert trigger.call_args[1]["context"] == {"order_id": "123"}
                channel.basic_ack.assert_called_once_with(1)

    def test_check_multiple_messages(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        bodies = [
            make_message(monitor.event.slug, {"seq": 1}),
            make_message(monitor.event.slug, {"seq": 2}),
        ]
        channel = make_channel_mock(bodies)
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            with patch.object(Event, "trigger") as trigger:
                agent.check()
                assert trigger.call_count == 2
                assert channel.basic_ack.call_count == 2

    def test_check_event_not_found_nacks(self, agent: AgentAMQP) -> None:
        body = make_message("nonexistent-event")
        channel = make_channel_mock([body])
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            with patch.object(Event, "trigger") as trigger:
                agent.check()
                trigger.assert_not_called()
                channel.basic_nack.assert_called_once()

    def test_check_invalid_json_nacks(self, agent: AgentAMQP) -> None:
        channel = make_channel_mock([b"not json"])
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            agent.check()
            channel.basic_nack.assert_called_once()

    def test_check_missing_event_field_nacks(self, agent: AgentAMQP) -> None:
        body = json.dumps({"type": "some.event", "data": {}}).encode()
        channel = make_channel_mock([body])
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            with patch.object(Event, "trigger") as trigger:
                agent.check()
                trigger.assert_not_called()
                channel.basic_nack.assert_called_once()

    def test_check_no_messages(self, agent: AgentAMQP) -> None:
        channel = make_channel_mock()
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            agent.check()
            channel.basic_ack.assert_not_called()
            channel.basic_nack.assert_not_called()

    def test_notify_calls_check(self, agent: AgentAMQP) -> None:
        with patch.object(agent, "check") as mock_check:
            agent.notify()
            mock_check.assert_called_once_with(notify=True, update=False)

    def test_custom_event_field(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        monitor.config["event_field"] = "type"
        body = json.dumps({"type": monitor.event.slug, "data": {"x": 1}}).encode()
        channel = make_channel_mock([body])
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            with patch.object(Event, "trigger") as trigger:
                agent.check()
                trigger.assert_called_once()
                assert trigger.call_args[1]["context"] == {"x": 1}
                channel.basic_ack.assert_called_once_with(1)

    def test_get_connection_params(self, agent: AgentAMQP) -> None:
        params = agent.get_connection_params()
        assert params.host == "rabbitmq.example.com"
        assert params.port == 5672
        assert params.virtual_host == "/"
        assert params.credentials is not None

    def test_ensure_queue_with_exchange(self, agent: AgentAMQP) -> None:
        channel = MagicMock()
        agent.ensure_queue(channel)
        channel.queue_declare.assert_called_once_with(queue="test_queue", durable=True)
        channel.queue_bind.assert_called_once_with(queue="test_queue", exchange="test_exchange", routing_key="test.key")

    def test_ensure_queue_without_exchange(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        monitor.config["exchange"] = ""
        channel = MagicMock()
        agent.ensure_queue(channel)
        channel.queue_declare.assert_called_once_with(queue="test_queue", durable=True)
        channel.queue_bind.assert_not_called()

    def test_consume_messages_respects_max(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        monitor.config["max_messages"] = 3
        channel = MagicMock()
        channel.consume.return_value = [
            (MagicMock(), MagicMock(), b"1"),
            (MagicMock(), MagicMock(), b"2"),
            (MagicMock(), MagicMock(), b"3"),
            (MagicMock(), MagicMock(), b"4"),
        ]
        messages = agent.consume_messages(channel)
        assert len(messages) == 3

    def test_consume_messages_timeout(self, agent: AgentAMQP) -> None:
        channel = MagicMock()
        channel.consume.return_value = [(None, None, None)]
        messages = agent.consume_messages(channel)
        assert len(messages) == 0

    def test_process_message_trigger_error(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        body = make_message(monitor.event.slug, {"x": 1})
        with patch.object(Event, "trigger", side_effect=Exception("DB error")):
            result = agent.process_message(body)
            assert result is False

    def test_process_message_success(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        body = make_message(monitor.event.slug, {"x": 1})
        with patch.object(Event, "trigger") as trigger:
            result = agent.process_message(body)
            assert result is True
            trigger.assert_called_once()
            assert trigger.call_args[1]["context"] == {"x": 1}

    def test_process_message_no_data_field(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        body = json.dumps({"event": monitor.event.slug}).encode()
        with patch.object(Event, "trigger") as trigger:
            result = agent.process_message(body)
            assert result is True
            trigger.assert_called_once()
            assert trigger.call_args[1]["context"] == {}

    def test_check_channel_fails_closes_connection(self, agent: AgentAMQP) -> None:
        conn = MagicMock()
        conn.channel.side_effect = Exception("channel failed")

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            agent.check()
            conn.close.assert_called_once()

    def test_changes_detected_closes_connection(self, agent: AgentAMQP) -> None:
        channel = MagicMock()
        channel.basic_get.return_value = (None, None, None)
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            agent.changes_detected()
            conn.close.assert_called_once()

    def test_connection_close_exception_handled(self, agent: AgentAMQP) -> None:
        channel = MagicMock()
        channel.consume.return_value = [(None, None, None)]
        conn = MagicMock()
        conn.channel.return_value = channel
        conn.close.side_effect = Exception("close failed")

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            agent.check()

    def test_process_message_event_does_not_exist(self, agent: AgentAMQP) -> None:
        body = make_message("does-not-exist")
        with patch.object(Event, "trigger") as trigger:
            result = agent.process_message(body)
            assert result is False
            trigger.assert_not_called()

    def test_check_connection_fails(self, agent: AgentAMQP) -> None:
        with (
            patch.object(agent, "get_connection_params"),
            patch.object(pika, "BlockingConnection", side_effect=Exception("connect failed")),
        ):
            agent.check()

    def test_check_process_message_error_nacks(self, agent: AgentAMQP, monitor: MagicMock) -> None:
        body = make_message(monitor.event.slug)
        channel = make_channel_mock([body])
        conn = MagicMock()
        conn.channel.return_value = channel

        with patch.object(agent, "get_connection_params"), patch.object(pika, "BlockingConnection", return_value=conn):
            with patch.object(agent, "process_message", side_effect=Exception("boom")):
                agent.check()
                channel.basic_nack.assert_called_once_with(1, requeue=False)
