from unittest.mock import patch

import pytest
from click.testing import CliRunner

from bitcaster.cli.__main__ import cli


@pytest.fixture
def runner():
    return CliRunner()


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
                result = runner.invoke(cli, ["run", "--processes", "4", "--threads", "2", "--loglevel", "debug"])

                assert result.exit_code == 0
                mock_main.assert_called_once()
                # We can check sys.argv if we want, but mock_main call is enough to prove it reached the end.
