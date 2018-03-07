# -*- coding: utf-8 -*-
"""
mercury / test_cli_configure
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from mercury.cli.commands.check import check
from mercury.config.environ import env


@pytest.mark.django_db
def test_cli_check(monkeypatch):
    runner = CliRunner(echo_stdin=True)
    config_file = Path(__file__).parent / 'sample.conf'
    monkeypatch.setitem(os.environ, 'BITCASTER_CONF', str(config_file))
    env.load_config(str(config_file))
    result = runner.invoke(check, obj={'config': os.environ['BITCASTER_CONF']})
    assert result.exit_code == 0, result.output
