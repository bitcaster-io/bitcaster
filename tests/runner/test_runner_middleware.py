from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest
from dramatiq import Message

if TYPE_CHECKING:
    from bitcaster.runner.middlewares import DbConnectionsMiddleware, WorkerHeartbeatMiddleware


@pytest.fixture
def middleware1() -> "WorkerHeartbeatMiddleware":
    from bitcaster.runner.middlewares import WorkerHeartbeatMiddleware

    return WorkerHeartbeatMiddleware()


@pytest.fixture
def middleware2() -> "DbConnectionsMiddleware":
    from bitcaster.runner.middlewares import DbConnectionsMiddleware

    return DbConnectionsMiddleware()


@pytest.fixture
def message() -> Message:
    return Message(
        message_id="id",
        queue_name="queue_name",
        actor_name="actor_name",
        args=(),
        kwargs={},
        options={"started_at": None},
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
