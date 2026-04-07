from unittest.mock import MagicMock, patch

import pytest

from bitcaster.cli.__main__ import cli
from bitcaster.runner.broker import ClickMiddleware


@pytest.mark.parametrize("autoreload", ["", "--autoreload"])
@pytest.mark.parametrize("debug", ["", "--debug"])
@pytest.mark.parametrize("pid_file", ["", "~temp.pid"])
@pytest.mark.parametrize(
    "verbosity",
    [
        pytest.param(0, id=""),
        pytest.param(1, id="-v"),
        pytest.param(2, id="-vv"),
    ],
)
@pytest.mark.parametrize("reset", ["", "--reset"])
def test_worker_run(runner, verbosity, pid_file, autoreload, monkeypatch, reset, debug):
    # worker.py calls dramatiq.cli.main()
    reloader = MagicMock()
    monkeypatch.setattr("django.utils.autoreload.run_with_reloader", reloader)
    args = ["run"]
    if verbosity > 0:
        args.extend(["-v"] * verbosity)
    if debug:
        args.extend(["--debug"])
    if reset:
        args.extend(["--reset"])
    if autoreload:
        args.extend(["--autoreload"])
    if pid_file:
        args.extend(["--pid-file", pid_file])

    with patch("dramatiq.cli.main") as mock_main:
        with patch("django.setup"):
            # It also imports bitcaster.config.dramatiq.broker and calls dramatiq.set_broker
            with patch("dramatiq.set_broker"):
                result = runner.invoke(cli, args)

    assert result.exit_code == 0, f"{result.output} {result.stderr}"
    if autoreload:
        reloader.assert_called_once()
    else:
        mock_main.assert_called_once()


def test_worker_run_options(runner):
    with patch("dramatiq.cli.main") as mock_main:
        with patch("django.setup"):
            with patch("dramatiq.set_broker"):
                result = runner.invoke(cli, ["run", "--processes", "4", "--threads", "2", "--debug"])

                assert result.exit_code == 0
                mock_main.assert_called_once()


def test_worker_run_ctrlc(runner):
    with patch("dramatiq.cli.main") as mock_main:
        mock_main.side_effect = KeyboardInterrupt
        with patch("django.setup"):
            with patch("dramatiq.set_broker"):
                result = runner.invoke(cli, ["run", "--processes", "4", "--threads", "2", "--debug"])

                assert result.exit_code == 0
                mock_main.assert_called_once()


def test_worker_clickmiddleware(runner, stub_dramatiq):
    import dramatiq.cli

    broker, worker = stub_dramatiq

    @dramatiq.actor
    def test(value):
        return value

    m = ClickMiddleware()
    broker.add_middleware(m)
    test.send("v")
    broker.join(test.queue_name)
    worker.join()
