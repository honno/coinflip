"""Assert test results from examples on our implementations"""
from math import isclose
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import NamedTuple
from typing import Union

import pytest

from coinflip import randtests

__all__ = ["Example", "examples"]

tests_path = Path(__file__).parent
data_path = tests_path / "data"


def e_expansion(n=1000000) -> Iterator[int]:
    """Generates bits of e

    Note
    ----
    Uses the same bit expansion that's included in NIST's `sts`
    """

    def genbits():
        with open(data_path / "e_expansion.txt") as f:
            for line in f:
                for x in line:
                    if x == "0" or x == "1":
                        bit = int(x)

                        yield bit

    e = genbits()
    for _ in range(n):
        yield next(e)


class Example(NamedTuple):
    """Contains template for a NIST example"""

    randtest: str
    bits: List[int]
    statistic: Union[int, float]
    p: float
    kwargs: Dict[str, Any] = {}


# fmt: off
examples = [
    Example(
        randtest="monobit",

        bits=[1, 0, 1, 1, 0, 1, 0, 1, 0, 1],

        statistic=.632455532,
        p=0.527089,
    ),
    Example(
        randtest="frequency_within_block",

        bits=[
            1, 1, 0, 0, 1, 0, 0, 1,
            0, 0, 0, 0, 1, 1, 1, 1,
            1, 1, 0, 1, 1, 0, 1, 0,
            1, 0, 1, 0, 0, 0, 1, 0,
            0, 0, 1, 0, 0, 0, 0, 1,
            0, 1, 1, 0, 1, 0, 0, 0,
            1, 1, 0, 0, 0, 0, 1, 0,
            0, 0, 1, 1, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 1, 0,
            0, 1, 1, 0, 0, 0, 1, 0,
            1, 0, 0, 0, 1, 0, 1, 1,
            1, 0, 0, 0,
        ],
        kwargs={
            "blocksize": 10
        },

        statistic=7.2,
        p=0.706438,
    ),
    Example(
        randtest="runs",

        bits=[
            1, 0, 0, 1, 1, 0, 1, 0,
            1, 1
        ],

        statistic=7,
        p=0.147232,
    ),
    Example(
        randtest="longest_runs",

        bits=[
            1, 1, 0, 0, 1, 1, 0, 0,
            0, 0, 0, 1, 0, 1, 0, 1,
            0, 1, 1, 0, 1, 1, 0, 0,
            0, 1, 0, 0, 1, 1, 0, 0,
            1, 1, 1, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 1, 0,
            0, 1, 0, 0, 1, 1, 0, 1,
            0, 1, 0, 1, 0, 0, 0, 1,
            0, 0, 0, 1, 0, 0, 1, 1,
            1, 1, 0, 1, 0, 1, 1, 0,
            1, 0, 0, 0, 0, 0, 0, 0,
            1, 1, 0, 1, 0, 1, 1, 1,
            1, 1, 0, 0, 1, 1, 0, 0,
            1, 1, 1, 0, 0, 1, 1, 0,
            1, 1, 0, 1, 1, 0, 0, 0,
            1, 0, 1, 1, 0, 0, 1, 0,
        ],


        statistic=4.882605,
        p=0.180609,
    ),
    Example(
        randtest="binary_matrix_rank",

        bits=[
            0, 1, 0, 1, 1, 0, 0, 1,
            0, 0, 1, 0, 1, 0, 1, 0,
            1, 1, 0, 1,
        ],
        kwargs={
            "matrix_dimen": (3, 3),
        },

        statistic=0.596953,
        p=0.741948,
    ),
    Example(
        randtest="binary_matrix_rank",

        bits=list(e_expansion(n=100000)),
        kwargs={
            "matrix_dimen": (32, 32),
        },

        statistic=1.2619656,
        p=0.532069,
    ),
    Example(
        # FAILING scipys fft produces slightly diff transformations to NIST's sts
        #         TODO  - check if examples succeed using NIST's fourier transforming
        #               - performance metrics on both solutions
        randtest="spectral",

        bits=[1, 0, 0, 1, 0, 1, 0, 0, 1, 1],

        statistic=-2.176429,
        p=0.029523,
    ),
    Example(
        randtest="spectral",

        bits=[
            1, 1, 0, 0, 1, 0, 0, 1,
            0, 0, 0, 0, 1, 1, 1, 1,
            1, 1, 0, 1, 1, 0, 1, 0,
            1, 0, 1, 0, 0, 0, 1, 0,
            0, 0, 1, 0, 0, 0, 0, 1,
            0, 1, 1, 0, 1, 0, 0, 0,
            1, 1, 0, 0, 0, 0, 1, 0,
            0, 0, 1, 1, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 1, 0,
            0, 1, 1, 0, 0, 0, 1, 0,
            1, 0, 0, 0, 1, 0, 1, 1,
            1, 0, 0, 0,
        ],

        statistic=-1.376494,
        p=0.168669,
    ),
    Example(
        randtest="non_overlapping_template_matching",

        bits=[
            1, 0, 1, 0, 0, 1, 0, 0,
            1, 0, 1, 1, 1, 0, 0, 1,
            0, 1, 1, 0
        ],
        kwargs={
            "template": [0, 0, 1],
            "nblocks": 2,
        },

        statistic=2.133333,
        p=0.344154,
    ),
    Example(
        # FAILING p off by ~0.07 if gammaincc(df/2, statistic/2) and df=2
        randtest="overlapping_template_matching",

        bits=[
            1, 0, 1, 1, 1, 0, 1, 1, 1, 1,
            0, 0, 1, 0, 1, 1, 0, 1, 1, 0,  # Modifed 2nd block of NIST example
            0, 1, 1, 1, 0, 0, 1, 0, 1, 1,  # originally had 1 match
            1, 0, 1, 1, 1, 1, 1, 0, 0, 0,  # now has 2 matches, as expected
            0, 1, 0, 1, 1, 0, 1, 0, 0, 1,
        ],
        kwargs={
            "template": [1, 1],
            "nblocks": 5,
            "df": 2,
        },

        statistic=3.167729,
        p=0.274932,
    ),
    Example(
        # FAILING Getting different tallies
        randtest="overlapping_template_matching",

        bits=list(e_expansion()),
        kwargs={
            "template": [1, 1, 1, 1, 1, 1, 1, 1, 1],
            "nblocks": 968,
        },

        statistic=8.965859,
        p=0.110434
    ),
    Example(
        randtest="maurers_universal",

        bits=[
            0, 1, 0, 1, 1, 0, 1, 0,
            0, 1, 1, 1, 0, 1, 0, 1,
            0, 1, 1, 1,
        ],
        kwargs={
            "blocksize": 2,
            "init_nblocks": 4,
        },

        statistic=1.1949875,
        p=0.767189,
    ),
    Example(
        randtest="linear_complexity",

        bits=list(e_expansion()),
        kwargs={
            "blocksize": 1000
        },

        statistic=2.700348,
        p=0.845406,
    ),
    Example(
        # FAILING - SP800-22's result is not replicated by sts
        #         - sts result matches our own
        randtest="serial",

        bits=[0, 0, 1, 1, 0, 1, 1, 1, 0, 1],
        kwargs={
            "blocksize": 3
        },

        # using the second p-value (+respective statistic)
        statistic=0.8,
        p=0.8805,
    ),
    Example(
        randtest="serial",

        bits=list(e_expansion()),
        kwargs={
            "blocksize": 2
        },

        # using the second p-value (+respective statistic)
        statistic=0.336400,
        p=0.561915,
    ),
    Example(
        randtest="approximate_entropy",

        bits=[0, 1, 0, 0, 1, 1, 0, 1, 0, 1],
        kwargs={
            "blocksize": 3
        },

        statistic=10.043859999999999,  # NIST erroneously had 0.502193
        p=0.261961,
    ),
    Example(
        randtest="approximate_entropy",

        bits=[
            1, 1, 0, 0, 1, 0, 0, 1,
            0, 0, 0, 0, 1, 1, 1, 1,
            1, 1, 0, 1, 1, 0, 1, 0,
            1, 0, 1, 0, 0, 0, 1, 0,
            0, 0, 1, 0, 0, 0, 0, 1,
            0, 1, 1, 0, 1, 0, 0, 0,
            1, 1, 0, 0, 0, 0, 1, 0,
            0, 0, 1, 1, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 1, 0,
            0, 1, 1, 0, 0, 0, 1, 0,
            1, 0, 0, 0, 1, 0, 1, 1,
            1, 0, 0, 0,
        ],
        kwargs={
            "blocksize": 2
        },

        statistic=5.550792,
        p=0.235301,
    ),
    Example(
        randtest="cusum",

        bits=[1, 0, 1, 1, 0, 1, 0, 1, 1, 1],

        statistic=4,
        p=0.4116588,
    ),
    Example(
        randtest="cusum",

        bits=[
            1, 1, 0, 0, 1, 0, 0, 1,
            0, 0, 0, 0, 1, 1, 1, 1,
            1, 1, 0, 1, 1, 0, 1, 0,
            1, 0, 1, 0, 0, 0, 1, 0,
            0, 0, 1, 0, 0, 0, 0, 1,
            0, 1, 1, 0, 1, 0, 0, 0,
            1, 1, 0, 0, 0, 0, 1, 0,
            0, 0, 1, 1, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 1, 0,
            0, 1, 1, 0, 0, 0, 1, 0,
            1, 0, 0, 0, 1, 0, 1, 1,
            1, 0, 0, 0,
        ],

        statistic=16,
        p=0.219194,
    ),
    Example(
        randtest="cusum",

        bits=[
            1, 1, 0, 0, 1, 0, 0, 1,
            0, 0, 0, 0, 1, 1, 1, 1,
            1, 1, 0, 1, 1, 0, 1, 0,
            1, 0, 1, 0, 0, 0, 1, 0,
            0, 0, 1, 0, 0, 0, 0, 1,
            0, 1, 1, 0, 1, 0, 0, 0,
            1, 1, 0, 0, 0, 0, 1, 0,
            0, 0, 1, 1, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 0, 0,
            1, 1, 0, 0, 0, 1, 1, 0,
            0, 1, 1, 0, 0, 0, 1, 0,
            1, 0, 0, 0, 1, 0, 1, 1,
            1, 0, 0, 0,
        ],
        kwargs={
            "reverse": True
        },

        statistic=19,
        p=0.114866,
    )

]


@pytest.mark.parametrize(Example._fields, examples)
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_examples(randtest, bits, statistic, p, kwargs):
    randtest_method = getattr(randtests, randtest)

    result = randtest_method(bits, **kwargs)

    if isinstance(statistic, float):
        assert isclose(result.statistic, statistic, rel_tol=0.05)
    elif isinstance(statistic, int):
        assert result.statistic == statistic

    assert isclose(result.p, p, abs_tol=0.005)
