# -*- coding: utf-8 -*-
"""
mercury / test_cli_configure
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from click.testing import CliRunner

from mercury.cli import cli


def test_hello_world():
    runner = CliRunner(env={'BITCASTER_CONF': "./aaaa"}, echo_stdin=True)
    with runner.isolated_filesystem():
        result = runner.invoke(cli)
        assert result.exit_code == 0
