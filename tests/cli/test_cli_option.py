# -*- coding: utf-8 -*-
from pathlib import Path

from click.testing import CliRunner

from bitcaster.cli.commands.option import _list
from bitcaster.config.environ import env


def test_cli_check():
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem():
        config_file = Path('./aaa')
        result = runner.invoke(_list, obj={'config': str(config_file),
                                           'env': env})
        assert result.exit_code == 0
