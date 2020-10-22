from click.testing import CliRunner

from coinflip import cli


def test_main():
    """Checks main command works"""
    runner = CliRunner()
    result = runner.invoke(cli.main, [])

    assert result.exit_code == 0


def test_example_run():
    """Checks example-run works"""
    runner = CliRunner()
    result = runner.invoke(cli.example_run, [])

    assert result.exit_code == 0
