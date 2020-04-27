import toml
from click.testing import CliRunner

from prng.cli import local_run


def nums2csv(table):
    lines = []
    for nums in table:
        line = ",".join(str(x) for x in nums)
        lines.append(line)

    return "\n".join(lines)


def test_localrun(fs):
    data = fs.create_file("data.csv")
    data_str = nums2csv([[0, 1, 2, 3, 4],
                         [1, 2, 3, 4, 5],
                         [2, 3, 4, 5, 6],
                         [3, 4, 5, 6, 7],
                         [4, 5, 6, 7, 8],
                         [5, 6, 7, 8, 9]])
    data.set_contents(data_str)

    spec = fs.create_file("spec.toml")
    spec_dict = {
        "dtype": "int"
    }
    spec_str = toml.dumps(spec_dict)
    spec.set_contents(spec_str)

    runner = CliRunner()
    result = runner.invoke(local_run, data.path, spec.path)

    assert result.exit_code == 0
