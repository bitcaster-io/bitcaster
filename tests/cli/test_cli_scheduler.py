import signal
import subprocess
from unittest import mock
from unittest.mock import MagicMock

import pytest

from bitcaster.cli.__main__ import cli

pytestmark = [pytest.mark.xdist_group(name="cli")]


@pytest.mark.parametrize("debug", ["", "--debug"])
@pytest.mark.parametrize("verbosity", [0, 1, 2, 3])
def test_scheduler_command(runner, monkeypatch, stub_dramatiq, verbosity, debug):
    run_scheduler = MagicMock()
    monkeypatch.setattr("bitcaster.runner.manager.scheduler", run_scheduler)
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


def test_scheduler_ctrlc(runner, monkeypatch, stub_dramatiq):
    from bitcaster.runner.manager import scheduler

    with mock.patch.object(scheduler, "start", side_effect=KeyboardInterrupt):
        result = runner.invoke(cli, ["scheduler"])
    assert result.exit_code == 1


def test_scheduler_run(runner, monkeypatch, stub_dramatiq):
    from bitcaster.runner.manager import scheduler

    with mock.patch.object(scheduler, "start", side_effect=KeyboardInterrupt):
        result = runner.invoke(cli, ["scheduler"])
    assert result.exit_code == 1


@pytest.mark.slow
@pytest.mark.xfail
def test_cron_command_interrupt(monkeypatch):
    """
    Test that the 'cron' management command can be gracefully
    interrupted with Control+C (SIGINT).
    """

    # Start the cron command as a subprocess
    process = subprocess.Popen(
        ["bc", "scheduler"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Let it run for 10 seconds. We expect it to still be running.
    try:
        process.wait(timeout=10)
        # If it finishes before the timeout, it's an unexpected exit.
        stdout, stderr = process.communicate()
        pytest.fail(
            f"Cron command exited prematurely with code {process.returncode}.\nStdout:\n{stdout}\nStderr:\n{stderr}"
        )
    except subprocess.TimeoutExpired:
        # This is the expected behavior. The process is still running.
        # Now, send the interrupt signal.
        process.send_signal(signal.SIGINT)

    # Wait for the process to terminate gracefully
    try:
        stdout, stderr = process.communicate(timeout=5)  # Give it 5s to shutdown
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()
        pytest.fail(f"Cron command did not terminate gracefully after SIGINT.\nStdout:\n{stdout}\nStderr:\n{stderr}")

    # Check that it exited cleanly.
    # A clean exit after catching SIGINT could be 0 or 1.
    # The main thing is that it terminates and logs a shutdown message.
    assert process.returncode is not None
    assert "Scheduler stopping..." in stdout
