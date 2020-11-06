from copy import copy
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
from hypothesis import HealthCheck
from hypothesis import settings
from hypothesis.stateful import Bundle
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import rule

from coinflip.cli import commands
from coinflip.cli import console

from .randtests.test_randtests import _mixedbits


class CliStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super(CliStateMachine, self).__init__()
        self.runner = CliRunner()

        # Make console dumb to tidy up captured stdout
        self.prev_console = copy(console)
        console.print = lambda *args, **kwargs: None

    randtest_results = Bundle("randtest_results")
    reports = Bundle("reports")

    @rule()
    def main(self):
        result = self.runner.invoke(commands.main, [])
        assert result.exit_code == 0

    @rule()
    def example_run(self):
        result = self.runner.invoke(commands.example_run, [])
        assert result.exit_code == 0

    @rule(target=randtest_results, sequence=_mixedbits())
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

        assert result.exit_code == 0

        return out.name

    @rule(path=randtest_results)
    def read(self, path):
        result = self.runner.invoke(commands.read, [path])
        assert result.exit_code == 0

    @rule(target=reports, path=randtest_results)
    def report(self, path):
        out = NamedTemporaryFile()

        result = self.runner.invoke(commands.report, [path, out.name])
        assert result.exit_code == 0

        return out.name

    def teardown(self):
        console.print = self.prev_console.print


TestCliStateMachine = CliStateMachine.TestCase  # top-level TestCase picked up by pytest
TestCliStateMachine.settings = settings(
    suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow],
    deadline=None,
)
