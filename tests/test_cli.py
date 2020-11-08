import webbrowser
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
from hypothesis import HealthCheck
from hypothesis import settings
from hypothesis.stateful import Bundle
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import rule

from coinflip.cli import commands
from coinflip.cli import console

from .strategies import mixedbits


class CliStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super(CliStateMachine, self).__init__()
        self.runner = CliRunner()

        console.print = noop
        webbrowser.open = noop

    randtest_results = Bundle("randtest_results")
    reports = Bundle("reports")

    @rule()
    def main(self):
        result = self.runner.invoke(commands.main, [])
        assert_success(result)

    @rule()
    def example_run(self):
        result = self.runner.invoke(commands.example_run, [])
        assert_success(result)

    @rule(target=randtest_results, sequence=mixedbits())
    def run(self, sequence):
        data = NamedTemporaryFile()
        out = NamedTemporaryFile()

        with data as f:
            for x in sequence:
                x_bin = str(x).encode("utf-8")
                line = x_bin + b"\n"
                f.write(line)

            f.seek(0)
            result = self.runner.invoke(commands.run, [f.name, out.name])

        assert_success(result)

        return out.name

    @rule(path=randtest_results)
    def read(self, path):
        result = self.runner.invoke(commands.read, [path])
        assert_success(result)

    @rule(target=reports, path=randtest_results)
    def report(self, path):
        out = NamedTemporaryFile()

        result = self.runner.invoke(commands.report, [path, out.name])
        assert_success(result)

        return out.name


TestCliStateMachine = CliStateMachine.TestCase  # top-level TestCase picked up by pytest
TestCliStateMachine.settings = settings(
    suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow],
    deadline=None,
)


def noop(*args, **kwargs):
    return None


def assert_success(result):
    assert result.exit_code == 0, result.stderr if result.stderr_bytes else str(result)
