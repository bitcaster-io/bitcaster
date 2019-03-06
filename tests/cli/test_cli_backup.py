# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from bitcaster.cli.commands.backup import backup, restore
from bitcaster.config.environ import env


@pytest.mark.django_db
def test_cli_backup_restore(subscription1):
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem():
        result = runner.invoke(backup, ['--filename', 'test_backup.json'],
                               obj={'env': env})
        assert result.exit_code == 0, result.output

        result = runner.invoke(restore, ['--filename', 'test_backup.json'], obj={'env': env})
        assert result.exit_code == 0, result.output

        result = runner.invoke(restore, ['--filename', 'test_backup.json',
                                         '-o', 'organization', '-w'],
                               obj={'env': env})
        assert result.exit_code == 0, result.output

        with Path('old_backup.json').open('w') as f:
            json.dump({'options': []}, f)

        result = runner.invoke(restore, ['--filename', f.name],
                               obj={'env': env})
        assert result.exit_code == 0, result.output

        result = runner.invoke(restore, ['--filename', f.name, '-i'],
                               obj={'env': env})
        assert result.exit_code == 0, result.output
