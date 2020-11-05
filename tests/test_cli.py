from random import getrandbits
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
from pytest import fixture

from coinflip.cli import commands


@fixture
def runner():
    return CliRunner()


def test_main(runner):
    result = runner.invoke(commands.main, [])

    assert result.exit_code == 0


def test_example_run(runner):
    result = runner.invoke(commands.example_run, [])

    assert result.exit_code == 0


def test_run(runner):
    data = NamedTemporaryFile()
    results_out = NamedTemporaryFile()
    sequence = [getrandbits(1) for _ in range(1000)]

    with data as f:
        for x in sequence:
            x_bin = str(x).encode("utf-8")
            line = x_bin + b"\n"
            f.write(line)

        f.seek(0)
        run_result = runner.invoke(commands.run, [f.name, results_out.name])

    assert run_result.exit_code == 0

    read_result = runner.invoke(commands.read, [results_out.name])
    assert read_result.exit_code == 0

    report_out = NamedTemporaryFile()
    report_result = runner.invoke(commands.report, [results_out.name, report_out.name])
    assert report_result.exit_code == 0
