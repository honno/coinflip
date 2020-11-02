from random import getrandbits
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
from pytest import fixture

from coinflip import _cli as cli


@fixture
def runner():
    return CliRunner()


def test_main(runner):
    result = runner.invoke(cli.main, [])

    assert result.exit_code == 0


def test_example_run(runner):
    runner = CliRunner()
    result = runner.invoke(cli.example_run, [])

    assert result.exit_code == 0


def test_run(runner):
    data = NamedTemporaryFile()
    out = NamedTemporaryFile()
    sequence = [getrandbits(1) for _ in range(1000)]

    with data as f:
        for x in sequence:
            x_bin = str(x).encode("utf-8")
            line = x_bin + b"\n"
            f.write(line)

        f.seek(0)
        result = runner.invoke(cli.run, [f.name, out.name])

    assert result.exit_code == 0
