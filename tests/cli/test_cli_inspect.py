from bitcaster.cli.__main__ import cli


def test_cli_queue(runner):
    result = runner.invoke(cli, ["queue"])
    assert result.exit_code == 2


def test_cli_inspect(runner):
    result = runner.invoke(cli, ["inspect"])
    assert result.exit_code == 0
