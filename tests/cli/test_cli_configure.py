# -*- coding: utf-8 -*-
from pathlib import Path

from click.testing import CliRunner

from bitcaster.cli.commands.configure import configure
from bitcaster.config.environ import env


def test_cli_configure():
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem():
        config_file = Path('./aaa')
        result = runner.invoke(configure, obj={'config': str(config_file),
                                               'env': env})
        assert result.exit_code == 0
        config = config_file.read_text()
        assert 'DATABASE_URL' in config
