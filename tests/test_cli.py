"""Model-based testing for the CLI"""
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
from rngtest.cli import main
from rngtest.store import data_dir

from .stattests.strategies import mixedbits

__all__ = ["test_main", "CliRoutes"]

r_storename = re.compile(
    r"Store name to be encoded as ([a-z\_0-9]+)\n", flags=re.IGNORECASE
)


@fixture(autouse=True, scope="module")
def module_setup_teardown():
    yield
    rmtree(data_dir)


# TODO doc
def test_main():
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code == 0


class CliRoutes(RuleBasedStateMachine):
    """State machine for routes taken via the CLI

    See Also
    --------
    RuleBasedStateMachine : Base class used to help define state machine
    """

    def __init__(self):
        super(CliRoutes, self).__init__()

        self.cli = CliRunner()

    storenames = Bundle("storenames")

    @rule(target=storenames, sequence=mixedbits())
    def add_store(self, sequence):
        datafile = NamedTemporaryFile()
        with datafile as f:
            for x in sequence:
                x_bin = str(x).encode("utf-8")
                line = x_bin + b"\n"
                f.write(line)

            f.seek(0)
            result = self.cli.invoke(cli.load, [f.name])

        store_name_msg = r_storename.search(result.stdout)
        store_name = store_name_msg.group(1)

        return store_name

    @rule(store_name=storenames)
    def find_storename_listed(self, store_name):
        result = self.cli.invoke(cli.ls)
        assert re.search(store_name, result.stdout)

    @rule(store_name=consumes(storenames))
    def remove_store(self, store_name):
        rm_result = self.cli.invoke(cli.rm, [store_name])
        assert rm_result.exit_code == 0

        ls_result = self.cli.invoke(cli.ls)
        assert not re.search(store_name, ls_result.stdout)


TestStore = CliRoutes.TestCase
