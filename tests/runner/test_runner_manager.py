from typing import TYPE_CHECKING

import dramatiq
import pytest
from dramatiq import Message, MessageProxy

if TYPE_CHECKING:
    from bitcaster.runner.manager import BackgroundManager


@pytest.fixture
def manager(broker) -> "BackgroundManager":
    from bitcaster.runner.manager import BackgroundManager

    return BackgroundManager()


@pytest.fixture
def message() -> MessageProxy:
    return MessageProxy(
        Message(
            message_id="id",
            queue_name="queue_name",
            actor_name="actor_name",
            args=(),
            kwargs={},
            options={"started_at": None},
        )
    )


@pytest.mark.xdist_group(name="runner")
def test_get_executor_name(manager):
    assert manager.get_executor_name()


@pytest.mark.xdist_group(name="runner")
def test_get_queue_sizes(broker, manager: "BackgroundManager"):
    @dramatiq.actor
    def test1():
        pass

    test1.send()
    assert manager.get_queue_sizes() == {"default": 1}


@pytest.mark.xdist_group(name="runner")
def test_get_queued_items(broker, manager: "BackgroundManager"):
    @dramatiq.actor
    def test2():
        pass

    test2.send()
    assert manager.get_queued_items()
    assert manager.get_queued_items()[0]["actor_name"] == "test2"


@pytest.mark.xdist_group(name="runner")
def test_reset(broker, manager: "BackgroundManager"):
    @dramatiq.actor
    def test3():
        pass

    test3.send()
    manager.reset()


@pytest.mark.xdist_group(name="runner")
def test_register_runner(manager: "BackgroundManager"):
    manager.register_runner()
    assert manager.get_runners()
    manager.unregister_runner()
    assert manager.get_runners() == {}


@pytest.mark.xdist_group(name="runner")
def test_get_runners(manager: "BackgroundManager"):
    assert manager.get_runners() == {}


@pytest.mark.xdist_group(name="runner")
def test_register_register_task(manager: "BackgroundManager", message):
    manager.register_task(message)

    assert (runners := manager.get_runners())
    assert len(runners[manager.name]["tasks"]) == 1
    assert runners[manager.name]["tasks"][0]["name"] == message.actor_name
    manager.unregister_task(message)
    assert (runners := manager.get_runners())
    assert len(runners[manager.name]["tasks"]) == 0


@pytest.mark.xdist_group(name="runner")
def test_scheduler_ping(manager: "BackgroundManager", message):
    manager.scheduler_ping()
    assert manager.get_runners()


@pytest.mark.xdist_group(name="runner")
def test_scheduler_info(manager: "BackgroundManager", message):
    manager.scheduler_info()
