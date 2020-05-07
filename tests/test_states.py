import re
from tempfile import NamedTemporaryFile

from click.testing import CliRunner
from hypothesis import settings
from hypothesis.stateful import Bundle
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import rule

from rngtest import cli

from .strategies import random_bits_strategy

r_storename = re.compile(
    "Store name to be encoded as ([a-z0-9]+)\n", flags=re.IGNORECASE
)


@settings(max_examples=5)
class StoreComparison(RuleBasedStateMachine):
    def __init__(self):
        super(StoreComparison, self).__init__()

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

    def teardown(self):
        pass


TestStore = StoreComparison.TestCase
