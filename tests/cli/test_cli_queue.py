from unittest import mock
from unittest.mock import MagicMock

from bitcaster.cli.__main__ import cli


def test_cli_queue(runner):
    result = runner.invoke(cli, ["queue"])
    assert result.exit_code == 2


def test_cli_queue_list(runner, stub_dramatiq):
    with mock.patch("bitcaster.runner.manager.BackgroundManager") as mocked:
        mock_instance = mocked.return_value

        mock_client = MagicMock()
        mock_instance.client = mock_client
        mock_instance.get_runners.return_value = {"runner1": {"last_seen": "2000-01-01", "tasks": [{"name": "task1"}]}}
        mock_instance.get_queue_sizes.return_value = {"default": 1}

        result = runner.invoke(cli, ["queue", "list"])
    assert result.exit_code == 0


def test_cli_queue_reset(runner, stub_dramatiq):
    with mock.patch("bitcaster.runner.manager.BackgroundManager") as mocked:
        mock_instance = mocked.return_value

        mock_client = MagicMock()
        mock_instance.client = mock_client
        mock_instance.get_runners.return_value = {"runner1": {"last_seen": "2000-01-01", "tasks": [{"name": "task1"}]}}
        mock_instance.get_queue_sizes.return_value = {"default": 1}

        result = runner.invoke(cli, ["queue", "reset"])
    assert result.exit_code == 0
