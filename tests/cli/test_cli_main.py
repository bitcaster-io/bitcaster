from click.testing import CliRunner

from bitcaster.cli import cli


def test_hello_world():
    runner = CliRunner(env={'BITCASTER_CONF': './aaaa'}, echo_stdin=True)
    with runner.isolated_filesystem():
        result = runner.invoke(cli)
        assert result.exit_code == 0
