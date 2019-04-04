import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from bitcaster.cli.commands.check import check

# from bitcaster.config.environ import env


@pytest.mark.django_db
def test_cli_check(monkeypatch, settings):
    settings.MEDIA_ROOT = os.path.curdir
    settings.STATIC_ROOT = os.path.curdir
    runner = CliRunner(echo_stdin=True)
    config_file = Path(__file__).parent / 'sample.conf'
    monkeypatch.setitem(os.environ, 'BITCASTER_CONF', str(config_file))
    # env.load_config(str(config_file))
    result = runner.invoke(check,
                           args=['--deploy'],
                           obj={'config': os.environ['BITCASTER_CONF']},
                           env={'BITCASTER_MEDIA_ROOT': '.',
                                'BITCASTER_STATC_ROOT': '.', })
    assert result.exit_code == 0, result.output
