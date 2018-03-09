# -*- coding: utf-8 -*-
from pathlib import Path

import pytest
from click.testing import CliRunner

from bitcaster.cli.commands.createuser import createuser
from bitcaster.config.environ import env


@pytest.mark.django_db
def test_cli_check():
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem():
        config_file = Path('./aaa')
        result = runner.invoke(createuser,
                               ['--email', 'test@test.com',
                                '--password', '123',
                                '--noinput'
                                ],
                               obj={'config': str(config_file),
                                    'env': env})
        assert result.exit_code == 0
