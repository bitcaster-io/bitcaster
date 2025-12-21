from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from django.conf import settings

from bitcaster.cli.__main__ import cli
from bitcaster.cli.scheduler import scheduler
from bitcaster.cli.worker import run


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_app():
    with patch("bitcaster.config.celery.app") as mock:
        yield mock


@pytest.fixture
def mock_cache():
    with patch("bitcaster.cli.scheduler.cache") as mock:
        yield mock


@pytest.fixture
def mock_worker_cache():
    with patch("bitcaster.cli.worker.cache") as mock:
        yield mock


@pytest.fixture
def mock_gethostname():
    with patch("bitcaster.cli.scheduler.gethostname", return_value="test-host") as mock:
        yield mock


@pytest.fixture
def mock_worker_gethostname():
    with patch("bitcaster.cli.worker.gethostname", return_value="test-host") as mock:
        yield mock


# Tests for scheduler command
def test_scheduler_starts_when_lock_acquired(runner, mock_app, mock_cache, mock_gethostname):
    mock_cache.add.return_value = True
    mock_beat_instance = MagicMock()
    mock_app.Beat.return_value = mock_beat_instance

    result = runner.invoke(scheduler)

    assert result.exit_code == 0
    assert "Starting dedicated Scheduler..." in result.output
    mock_cache.add.assert_called_once()
    mock_app.Beat.assert_called_once()
    mock_beat_instance.run.assert_called_once()
    mock_cache.delete.assert_called_once()


def test_scheduler_exits_when_lock_held(runner, mock_app, mock_cache, mock_gethostname):
    mock_cache.add.return_value = False

    result = runner.invoke(scheduler)

    assert result.exit_code == 0
    assert "Another Scheduler instance is already running. Exiting." in result.output
    mock_cache.add.assert_called_once()
    mock_app.Beat.assert_not_called()


# Tests for worker run command
def test_worker_run_defaults(runner, mock_app, mock_worker_cache, mock_worker_gethostname):
    mock_worker_cache.add.return_value = True
    mock_worker_instance = MagicMock()
    mock_app.Worker.return_value = mock_worker_instance

    result = runner.invoke(run)

    assert result.exit_code == 0
    assert "Acquired lock. Starting Scheduler." in result.output
    mock_app.Worker.assert_called_once()
    _, kwargs = mock_app.Worker.call_args
    assert kwargs["beat"] is True
    assert kwargs["scheduler"] == settings.CELERY_BEAT_SCHEDULER
    mock_worker_instance.start.assert_called_once()


def test_worker_run_no_scheduler(runner, mock_app, mock_worker_cache, mock_worker_gethostname):
    mock_worker_instance = MagicMock()
    mock_app.Worker.return_value = mock_worker_instance

    result = runner.invoke(run, ["--no-scheduler"])

    assert result.exit_code == 0
    mock_worker_cache.add.assert_not_called()
    mock_app.Worker.assert_called_once()
    _, kwargs = mock_app.Worker.call_args
    assert kwargs["beat"] is False


def test_worker_run_scheduler_lock_held(runner, mock_app, mock_worker_cache, mock_worker_gethostname):
    mock_worker_cache.add.return_value = False
    mock_worker_instance = MagicMock()
    mock_app.Worker.return_value = mock_worker_instance

    result = runner.invoke(run, ["--scheduler"])

    assert result.exit_code == 0
    assert "Scheduler lock held by another worker. Skipping Scheduler." in result.output
    mock_app.Worker.assert_called_once()
    _, kwargs = mock_app.Worker.call_args
    assert kwargs["beat"] is False


def test_worker_run_with_queues(runner, mock_app, mock_worker_cache, mock_worker_gethostname):
    mock_worker_cache.add.return_value = True
    mock_worker_instance = MagicMock()
    mock_app.Worker.return_value = mock_worker_instance

    result = runner.invoke(run, ["--queues", "queue1,queue2"])

    assert result.exit_code == 0
    mock_app.Worker.assert_called_once()
    _, kwargs = mock_app.Worker.call_args
    assert kwargs["queues"] == "queue1,queue2"


# Tests for main cli
def test_cli_main(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "run" in result.output
    assert "scheduler" in result.output
