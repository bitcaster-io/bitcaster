# -*- coding: utf-8 -*-
from pathlib import Path

from click.testing import CliRunner

from bitcaster.cli.commands.upgrade import upgrade
from bitcaster.config.environ import env


def test_cli_upgrade(db):
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem():
        config_file = Path('./aaa')
        result = runner.invoke(upgrade, ['--no-input'],
                               obj={'config': str(config_file),
                                    'env': env})
        assert result.exit_code == 0, result.output
