import re
from datetime import timedelta
from shutil import rmtree
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
from hypothesis import settings
from hypothesis.stateful import Bundle
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import consumes
from hypothesis.stateful import rule
from pytest import fixture

from rngtest import cli
from rngtest.store import data_dir

from .stattests.test_compare_implementations import mixedbits

__all__ = ["CliRoutes"]

r_storename = re.compile(
    r"Store name to be encoded as ([a-z\_0-9]+)\n", flags=re.IGNORECASE
)


@fixture(autouse=True, scope="module")
def module_setup_teardown():
    yield
    rmtree(data_dir)


class CliRoutes(RuleBasedStateMachine):
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


CliRoutes.TestCase.settings = settings(
    max_examples=1, stateful_step_count=1, deadline=timedelta(milliseconds=2000)
)


TestStore = CliRoutes.TestCase
