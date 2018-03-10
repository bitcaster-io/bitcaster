# -*- coding: utf-8 -*-
from pathlib import Path

from click.testing import CliRunner

from bitcaster.cli.commands.backup import backup, restore
from bitcaster.config.environ import env


def test_cli_backup(system_channel):
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem():
        config_file = Path('./aaa')
        result = runner.invoke(backup,
                               ['--file', 'aa.json', ],
                               obj={'config': str(config_file),
                                    'env': env})
        assert result.exit_code == 0


def test_cli_restore(db):
    runner = CliRunner(echo_stdin=True)
    config_file = Path('./aaa')
    dumpfile = Path(__file__).parent / 'backup.json'
    result = runner.invoke(restore,
                           ['--file', str(dumpfile)],
                           obj={'config': str(config_file),
                                'env': env})
    assert result.exit_code == 0, result.output
