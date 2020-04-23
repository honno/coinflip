from random import random

import toml
from click.testing import CliRunner

from prng.cli import serialize


def test_file_reads(fs):
    data = fs.create_file("data.csv")
    spec = fs.create_file("spec.toml")

    rand_list = []
    for _ in range(100):
        rand_list.append(str(random()))
    data.set_contents("\n".join(rand_list))

    spec_dict = {
        "type": "float",
    }
    spec_str = toml.dumps(spec_dict)
    spec.set_contents(spec_str)

    runner = CliRunner()
    result = runner.invoke(serialize, [data.path, spec.path])

    assert result.exit_code == 0
    assert result.output == spec_str + "\n"
