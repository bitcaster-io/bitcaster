from typing import TYPE_CHECKING
from unittest import mock

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


@pytest.mark.xdist_group(name="runner")
def test_manager_actors(manager: "BackgroundManager", message):
    from bitcaster.runner.broker import broker

    with mock.patch.object(broker, "get_declared_actors", wraps=broker.get_declared_actors) as m:
        assert manager.actors
        assert m.call_count == 1
    with mock.patch.object(broker, "get_declared_actors", wraps=broker.get_declared_actors) as m:
        assert manager.actors
        assert m.call_count == 0


@pytest.mark.xdist_group(name="runner")
def test_manager_get_queue_sizes(manager: "BackgroundManager", message):
    from bitcaster.runner.broker import broker

    manager._actors = []
    with mock.patch.object(broker, "get_declared_actors", wraps=broker.get_declared_actors) as m:
        assert manager.actors
        assert m.call_count == 1

    with mock.patch.object(broker, "get_declared_actors", wraps=broker.get_declared_actors) as m:
        assert manager.actors
        assert m.call_count == 0


@pytest.mark.xdist_group(name="runner")
def test_get_queue_sizes_unknown_key_type(manager: "BackgroundManager", broker):
    @dramatiq.actor
    def test_unknown_type():
        pass

    queue_key = f"{broker.namespace}:default.msgs"
    broker.client.delete(queue_key)
    broker.client.set(queue_key, "dummy")
    result = manager.get_queue_sizes()
    assert result == {"default": 0}


@pytest.mark.xdist_group(name="runner")
def test_get_queued_items_list_type(manager: "BackgroundManager", broker):
    @dramatiq.actor
    def test_list_items():
        pass

    test_list_items.send()
    items = manager.get_queued_items()
    assert len(items) == 1
    assert items[0]["actor_name"] == "test_list_items"


@pytest.mark.xdist_group(name="runner")
def test_get_queued_items_no_key(manager: "BackgroundManager", broker):
    @dramatiq.actor
    def test_no_key():
        pass

    items = manager.get_queued_items()
    assert items == []


@pytest.mark.xdist_group(name="runner")
def test_get_runners_stale_no_last_seen(manager: "BackgroundManager"):
    stale_name = "stale_runner_no_ts"
    manager.client.sadd("background:runners", stale_name)
    runners = manager.get_runners()
    assert stale_name not in runners
    assert stale_name not in manager.client.smembers("background:runners")


@pytest.mark.xdist_group(name="runner")
def test_get_runners_stale_over_one_hour(manager: "BackgroundManager"):
    from datetime import UTC, datetime, timedelta

    stale_name = "stale_runner_old"
    old_ts = (datetime.now(UTC) - timedelta(hours=2)).timestamp()
    manager.client.sadd("background:runners", stale_name)
    manager.client.set(f"background:runners:{stale_name}:last_seen", old_ts)
    runners = manager.get_runners()
    assert stale_name in runners
    assert runners[stale_name]["alive"] is False
    assert stale_name not in manager.client.smembers("background:runners")


@pytest.mark.xdist_group(name="runner")
def test_get_task_last_run_missing(manager: "BackgroundManager"):
    result = manager.get_task_last_run("nonexistent_actor")
    assert result is None


@pytest.mark.xdist_group(name="runner")
def test_get_task_last_run_success(manager: "BackgroundManager"):
    from datetime import UTC, datetime

    actor = "test_actor_success"
    now = datetime.now(UTC)
    manager.client.set(f"background:runners:{manager.name}:{actor}:last_run", now.timestamp())
    result = manager.get_task_last_run(actor)
    assert result is not None
    assert abs((result - now).total_seconds()) < 1


@pytest.mark.xdist_group(name="runner")
def test_get_task_last_run_invalid_data(manager: "BackgroundManager"):
    manager.client.set(f"background:runners:{manager.name}:nonexistent_actor:last_run", b"not_a_number")
    result = manager.get_task_last_run("nonexistent_actor")
    assert result is None


@pytest.mark.xdist_group(name="runner")
def test_get_task_last_run_none_value(manager: "BackgroundManager"):
    """Test when Redis returns None for the key."""
    manager.client.delete(f"background:runners:{manager.name}:missing_actor:last_run")
    result = manager.get_task_last_run("missing_actor")
    assert result is None


@pytest.mark.xdist_group(name="runner")
def test_init_scheduler_updates_existing(broker, settings):
    from bitcaster.models import Task
    from bitcaster.runner.manager import SCHEDULER, init_scheduler

    Task.objects.all().delete()
    sid = "scan_occurrences"
    config = SCHEDULER[sid]

    task = Task.objects.create(slug=sid, name="old_name", trigger_config={}, func="old.func", trigger="interval")
    init_scheduler()
    task.refresh_from_db()
    assert task.func == config["func"]
    assert task.trigger == config["trigger"]


@pytest.mark.xdist_group(name="runner")
def test_init_scheduler_creates_new(broker, settings):
    from bitcaster.models import Task
    from bitcaster.runner.manager import SCHEDULER, init_scheduler

    Task.objects.all().delete()
    sid = "scan_occurrences"
    init_scheduler()
    task = Task.objects.get(slug=sid)
    assert task.name == sid
    assert task.func == SCHEDULER[sid]["func"]


@pytest.mark.xdist_group(name="runner")
def test_get_all_tasks(manager: "BackgroundManager"):
    all_tasks = manager.get_all_tasks()
    assert isinstance(all_tasks, dict)
    assert len(all_tasks) > 0


@pytest.mark.xdist_group(name="runner")
def test_update_task(manager: "BackgroundManager", message):
    manager.update_task(message.actor_name)
    key = f"background:runners:{manager.name}:{message.actor_name}:last_run"
    assert manager.client.exists(key)


@pytest.mark.xdist_group(name="runner")
def test_reset_with_keys(manager: "BackgroundManager"):
    manager.client.set("background:test_key", "value")
    manager.reset()
    assert not manager.client.exists("background:test_key")


@pytest.mark.xdist_group(name="runner")
def test_scheduler_info_no_ping(manager: "BackgroundManager"):
    manager.client.delete("scheduler:alive")
    info = manager.scheduler_info()
    assert info["status"] is False
    assert info["seen"] == ""
