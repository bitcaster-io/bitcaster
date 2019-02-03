# -*- coding: utf-8 -*-
from click.testing import CliRunner

from bitcaster.cli.commands.createuser import createuser


def test_cli_configure():
    runner = CliRunner(echo_stdin=True)
    with runner.isolated_filesystem():
        result = runner.invoke(createuser,
                               args=['--email', 'user@example.com',
                                     '--password', 'Password!'],
                               obj={})
        assert result.exit_code == 0
