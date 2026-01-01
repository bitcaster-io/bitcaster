from unittest.mock import MagicMock

from bitcaster.cli.__main__ import cli


def test_scheduler_command(runner, monkeypatch, stub_dramatiq):
    run_scheduler = MagicMock()
    monkeypatch.setattr("bitcaster.runner.manager.scheduler", run_scheduler)
    result = runner.invoke(cli, ["scheduler", "-vvvvv"])
    assert result.exit_code == 0


def test_scheduler_command_autoreload(runner, monkeypatch, stub_dramatiq):
    reloader = MagicMock()
    monkeypatch.setattr("django.utils.autoreload.run_with_reloader", reloader)
    result = runner.invoke(cli, ["scheduler", "--autoreload"])
    assert result.exit_code == 0
    reloader.assert_called_once()
