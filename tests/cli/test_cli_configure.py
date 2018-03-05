# -*- coding: utf-8 -*-
"""
mercury / test_cli_configure
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from pathlib import Path

from click.testing import CliRunner

from mercury.cli.commands.configure import configure
from mercury.config.environ import env


def test_hello_world():
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem():
        config_file = Path('./aaa')
        result = runner.invoke(configure, obj={'config': str(config_file),
                                               'env': env})
        assert result.exit_code == 0
        config = config_file.read_text()
        assert 'DATABASE_URL' in config
