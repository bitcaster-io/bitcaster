from typing import TYPE_CHECKING

import dramatiq
import pytest
from dramatiq import Message

if TYPE_CHECKING:
    from bitcaster.runner.manager import BackgroundManager


@pytest.fixture
def manager(broker) -> "BackgroundManager":
    from bitcaster.runner.manager import BackgroundManager

    return BackgroundManager()


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


def test_get_queue_sizes(broker, manager: "BackgroundManager"):
    @dramatiq.actor
    def test1():
        pass

    test1.send()
    assert manager.get_queue_sizes() == {"default": 1}


def test_get_queued_items(broker, manager: "BackgroundManager"):
    @dramatiq.actor
    def test2():
        pass

    test2.send()
    assert manager.get_queued_items()
    assert manager.get_queued_items()[0]["actor_name"] == "test2"


def test_reset(broker, manager: "BackgroundManager"):
    @dramatiq.actor
    def test3():
        pass

    test3.send()
    manager.reset()


def test_register_runner(broker, manager: "BackgroundManager"):
    assert manager.register_runner()


def test_unregister_runner(broker, manager: "BackgroundManager"):
    manager.register_runner()
    manager.unregister_runner()


def test_get_runners(broker, manager: "BackgroundManager"):
    assert manager.get_runners() == {}


def test_register_task(broker, manager: "BackgroundManager", message):
    manager.register_task(message)
    manager.unregister_task(message.message_id)


def test_scheduler_ping(broker, manager: "BackgroundManager", message):
    manager.scheduler_ping()


def test_scheduler_info(broker, manager: "BackgroundManager", message):
    manager.scheduler_info()
