import re
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
from hypothesis import settings
from hypothesis.stateful import Bundle
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import consumes
from hypothesis.stateful import rule

from rngtest import cli

from .strategies import random_bits_strategy

r_storename = re.compile(
    "Store name to be encoded as ([a-z0-9]+)\n", flags=re.IGNORECASE
)


class CliRoutes(RuleBasedStateMachine):
    def __init__(self):
        super(CliRoutes, self).__init__()

        self.cli = CliRunner()

    storenames = Bundle("storenames")

    @rule(target=storenames, sequence=random_bits_strategy)
    def add_store(self, sequence):
        datafile = NamedTemporaryFile()
        with datafile as f:
            for x in sequence:
                x_bin = str(x).encode("utf-8")
                f.write(x_bin)

            f.seek(0)
            result = self.cli.invoke(cli.load, [f.name])

        storename_msg = r_storename.search(result.stdout)
        storename = storename_msg.group(1)

        return storename

    @rule(name=storenames)
    def find_storename_listed(self, name):
        result = self.cli.invoke(cli.ls)
        assert re.search(name, result.stdout)

    @rule(name=consumes(storenames))
    def remove_store(self, name):
        rm_result = self.cli.invoke(cli.rm, [name])
        assert rm_result.exit_code == 0

        ls_result = self.cli.invoke(cli.ls)
        assert not re.search(name, ls_result.stdout)

    def teardown(self):
        pass


CliRoutes.TestCase.settings = settings(
    max_examples=1  # TODO work out sensible examples no.
)


TestStore = CliRoutes.TestCase
