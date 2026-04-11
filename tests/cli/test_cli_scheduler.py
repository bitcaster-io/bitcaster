import datetime
from typing import TYPE_CHECKING
from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from apscheduler.schedulers.base import STATE_RUNNING, STATE_STOPPED
from freezegun import freeze_time
from testutils.perms import configure_model

from bitcaster.cache.manager import epoch
from bitcaster.cli.__main__ import cli

if TYPE_CHECKING:
    from apscheduler.schedulers.blocking import BlockingScheduler

    from bitcaster.models import Task


pytestmark = [pytest.mark.xdist_group(name="cli")]


@pytest.fixture
def scheduler(monkeypatch) -> "BlockingScheduler":
    from bitcaster.runner.manager import BlockingScheduler

    s = BlockingScheduler()
    monkeypatch.setattr("bitcaster.runner.manager.scheduler", s)
    monkeypatch.setattr("bitcaster.cli.scheduler.scheduler", s)
    monkeypatch.setattr("bitcaster.cli.scheduler.last_round", epoch.astimezone(datetime.UTC))
    return s


@pytest.fixture
def task1() -> "Task":
    from testutils.factories import TaskFactory

    return TaskFactory.create(
        active=True,
        func="bitcaster.runner.tasks.scan_occurrences",
        trigger="interval",
        trigger_config={"seconds": 1},
    )


@pytest.fixture
def task2() -> "Task":
    from testutils.factories import TaskFactory

    return TaskFactory.create(
        active=True, func="bitcaster.runner.tasks.monitor_run", trigger="interval", trigger_config={"seconds": 1}
    )


@pytest.fixture
def task3() -> "Task":
    from testutils.factories import TaskFactory

    return TaskFactory.create(
        active=False, func="bitcaster.runner.tasks.purge_occurrences", trigger="interval", trigger_config={"seconds": 1}
    )


def test_scheduler_queue(task: "Task"):
    from bitcaster.cli.scheduler import queue

    queue(task.id)


def test_scheduler_queue_security_alert(task: "Task", monkeypatch):
    from bitcaster.cli.scheduler import queue

    # Mock BackgroundManager to return an empty list of allowed actors
    mock_manager = MagicMock()
    mock_manager.get_all_tasks.return_value = {}
    monkeypatch.setattr("bitcaster.cli.scheduler.BackgroundManager", lambda: mock_manager)

    with patch("bitcaster.cli.scheduler.logger") as mock_logger:
        queue(task.id)
        mock_logger.error.assert_called_once()
        assert "Security Alert" in mock_logger.error.call_args[0][0]


def test_scheduler_healthcheck(runner, monkeypatch, stub_dramatiq):
    from bitcaster.cli.scheduler import healthcheck

    healthcheck()


@pytest.mark.parametrize("debug", ["", "--debug"])
@pytest.mark.parametrize("verbosity", [0, 1, 2, 3])
def test_scheduler_command(runner, monkeypatch, stub_dramatiq, verbosity, debug, task1, task2):
    run_scheduler = MagicMock()
    monkeypatch.setattr("bitcaster.cli.scheduler.scheduler", run_scheduler)
    args = ["scheduler"]
    if verbosity:
        args.extend(["-v"] * verbosity)
    if debug:
        args.append(debug)
    result = runner.invoke(cli, args)
    assert result.exit_code == 0


def test_scheduler_command_autoreload(runner, monkeypatch, stub_dramatiq):
    reloader = MagicMock()
    monkeypatch.setattr("django.utils.autoreload.run_with_reloader", reloader)
    result = runner.invoke(cli, ["scheduler", "--autoreload"])
    assert result.exit_code == 0
    reloader.assert_called_once()


@pytest.mark.parametrize("verbose", [0, 1, 2, 3])
@pytest.mark.parametrize("debug", [True, False])
def test_run_scheduler(scheduler, verbose, debug, monkeypatch):
    from bitcaster.cli.scheduler import run_scheduler

    with mock.patch.object(scheduler, "start"):
        run_scheduler(verbose, debug)


def test_inspect_jobs(scheduler, monkeypatch, task1):
    from bitcaster.cli.scheduler import inspect_jobs

    with freeze_time("2026-12-31 10:00:00"):
        inspect_jobs()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1


def test_inspect_jobs_add_inactive(scheduler, monkeypatch, task3):
    from bitcaster.cli.scheduler import inspect_jobs

    inspect_jobs()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1
    assert not scheduler.get_job(task3.slug).next_run_time


def test_inspect_jobs_update_pause_inactive(scheduler, monkeypatch, task1):
    from bitcaster.cli.scheduler import inspect_jobs

    inspect_jobs()
    job1 = scheduler.get_job(task1.slug)
    job1.resume()
    with configure_model(task1, active=False):
        inspect_jobs()


def test_inspect_jobs_update_resume_reactivated(scheduler, monkeypatch, task3):
    from bitcaster.cli.scheduler import inspect_jobs

    inspect_jobs()
    with configure_model(task3, active=True):
        inspect_jobs()


def test_inspect_jobs_raise_exception(scheduler, monkeypatch, task3):
    from bitcaster.cli.scheduler import inspect_jobs

    monkeypatch.setattr("apscheduler.job.Job.pause", lambda s: 1 / 0)
    inspect_jobs()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 1


@pytest.mark.parametrize("state", [STATE_RUNNING, STATE_STOPPED])
def test_cron_command_interrupt(scheduler: "BlockingScheduler", monkeypatch, state):
    from bitcaster.cli.scheduler import run_scheduler

    monkeypatch.setattr("bitcaster.cli.scheduler.inspect_jobs", lambda: True)
    with mock.patch.object(scheduler, "shutdown"):
        with mock.patch.object(scheduler, "add_job"):
            with mock.patch.object(scheduler, "start", side_effect=KeyboardInterrupt):
                with mock.patch.object(scheduler, "state", state):
                    run_scheduler(0, 0)
