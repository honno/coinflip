import toml
from click.testing import CliRunner

from prng.cli import local_run


def table2csv(table):
    lines = []
    for nums in table:
        line = ",".join(str(x) for x in nums)
        lines.append(line)

    return "\n".join(lines)


def localrun(fs, table, specdict):
    data = fs.create_file("data.csv")
    datastr = table2csv(table)
    data.set_contents(datastr)

    spec = fs.create_file("spec.toml")
    specstr = toml.dumps(specdict)
    spec.set_contents(specstr)

    result = CliRunner().invoke(local_run, [data.path, spec.path])

    return result


fourbyfour = [[0, 1], [2, 3]]


def test_table_noprofiles(fs):
    specdict = {"dtype": "int", "concat": "columns"}
    result = localrun(fs, fourbyfour, specdict)

    assert result.exit_code == 0


def test_table_profiles(fs):
    specdict = {
        "dtype": "int",
        "by-col": {"concat": "columns"},
        "by-row": {"concat": "rows"},
    }
    result = localrun(fs, fourbyfour, specdict)

    assert result.exit_code == 0
