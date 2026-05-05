from typing import TYPE_CHECKING, Any

from dramatiq import Actor, Message, MessageProxy
from jinja2.utils import import_string

import pytest
from unittest.mock import Mock

if TYPE_CHECKING:
    from bitcaster.runner.middlewares import ClickMiddleware, DbConnectionsMiddleware, WorkerHeartbeatMiddleware


@pytest.fixture
def middleware1() -> "WorkerHeartbeatMiddleware":
    from bitcaster.runner.middlewares import WorkerHeartbeatMiddleware

    return WorkerHeartbeatMiddleware()


@pytest.fixture
def middleware2() -> "DbConnectionsMiddleware":
    from bitcaster.runner.middlewares import DbConnectionsMiddleware

    return DbConnectionsMiddleware()


@pytest.fixture
def middleware3() -> "ClickMiddleware":
    from bitcaster.runner.middlewares import ClickMiddleware

    return ClickMiddleware()


@pytest.fixture
def message() -> MessageProxy:
    return MessageProxy(
        Message(
            message_id="id",
            queue_name="queue_name",
            actor_name="bitcaster.runner.tasks.monitor_run",
            args=(),
            kwargs={},
            options={"started_at": None, "logging": False},
        )
    )


@pytest.fixture
def actor(message) -> Actor[Any, Any]:
    return Actor(
        fn=import_string(message.actor_name).fn,
        broker=Mock(actors=[]),
        actor_name=message.actor_name,
        queue_name=message.queue_name,
        priority=1,
        options={},
    )


def test_m1_before_process_message(middleware1: "WorkerHeartbeatMiddleware", message):
    middleware1.before_process_message(Mock(), message)


def test_m1_after_process_message(middleware1: "WorkerHeartbeatMiddleware", message):
    middleware1.after_process_message(Mock(), message)


def test_m2__before_process_message(middleware2: "DbConnectionsMiddleware", message):
    middleware2.before_process_message(Mock(), message)


def test_m2_after_process_message(middleware2: "DbConnectionsMiddleware", message):
    middleware2.after_process_message(Mock(), message)


def test_m2_before_worker_shutdown(middleware2: "DbConnectionsMiddleware", message):
    middleware2.before_worker_shutdown(Mock(), message)


def test_m3_before_process_message(middleware3: "ClickMiddleware", message: MessageProxy, monkeypatch):
    middleware3.before_process_message(Mock(), message)


@pytest.mark.parametrize("logging", [True, False])
def test_m3_after_process_message(middleware3: "ClickMiddleware", message: MessageProxy, actor, logging):
    message.options["logging"] = logging
    broker = Mock(actors=[])

    broker.get_actor = lambda x: actor
    broker.actors = [actor]

    middleware3.before_process_message(broker, message)
    middleware3.after_process_message(broker, message)


def test_m3_after_worker_boot(middleware3: "ClickMiddleware", message: MessageProxy):
    middleware3.after_worker_boot(Mock(), message)
