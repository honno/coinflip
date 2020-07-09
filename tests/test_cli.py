import re
from shutil import rmtree
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
from hypothesis.stateful import Bundle
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import consumes
from hypothesis.stateful import rule
from pytest import fixture

from rngtest import cli
from rngtest.store import data_dir

from .randtests.strategies import mixedbits

__all__ = ["test_main", "CliRoutes"]


@fixture(autouse=True, scope="module")
def module_setup_teardown():
    """Clears user data directory on teardown"""
    yield
    rmtree(data_dir)


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


r_storename = re.compile(
    r"Store name to be encoded as ([a-z\_0-9]+)\n", flags=re.IGNORECASE
)


# TODO add more rules to represent all CLI functionality
class CliRoutes(RuleBasedStateMachine):
    """State machine for routes taken via the CLI

    Specifies a state machine representation of the CLI to be used in
    model-based testing.

    Notes
    -----
    Read the `hypothesis stateful guide
    <https://hypothesis.readthedocs.io/en/latest/stateful.html>`_ for help on
    understanding and modifying this state machine.
    """

    def __init__(self):
        super(CliRoutes, self).__init__()

        self.runner = CliRunner()

    stores = Bundle("stores")

    @rule(target=stores, sequence=mixedbits())
    def add_store(self, sequence):
        """Mock data files and load them into initialised stores"""
        datafile = NamedTemporaryFile()
        with datafile as f:
            for x in sequence:
                x_bin = str(x).encode("utf-8")
                line = x_bin + b"\n"
                f.write(line)

            f.seek(0)
            result = self.runner.invoke(cli.load, [f.name])

        store_msg = r_storename.search(result.stdout)
        store = store_msg.group(1)

        return store

    @rule(store=stores)
    def find_store_listed(self, store):
        """Check if initialised stores are listed"""
        result = self.runner.invoke(cli.ls)
        assert re.search(store, result.stdout)

    @rule(store=consumes(stores))
    def remove_store(self, store):
        """Remove stores and check they're not listed"""
        rm_result = self.runner.invoke(cli.rm, [store])
        assert rm_result.exit_code == 0

        ls_result = self.runner.invoke(cli.ls)
        assert not re.search(store, ls_result.stdout)


TestCliRoutes = CliRoutes.TestCase  # top-level TestCase to be picked up by pytest
