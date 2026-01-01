from unittest.mock import patch

from bitcaster.cli.__main__ import cli
from bitcaster.cli.worker import ClickMiddleware


def test_worker_run(runner):
    # worker.py calls dramatiq.cli.main()
    with patch("dramatiq.cli.main") as mock_main:
        with patch("django.setup"):
            # It also imports bitcaster.config.dramatiq.broker and calls dramatiq.set_broker
            with patch("dramatiq.set_broker"):
                result = runner.invoke(cli, ["run"])

    assert result.exit_code == 0
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
