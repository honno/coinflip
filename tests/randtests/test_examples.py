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

__all__ = ["Example", "MultiExample", "examples", "multi_examples"]

tests_path = Path(__file__).parent
data_path = tests_path / "data"


def e_expansion(n=1000000) -> Iterator[int]:
    """Generates bits of e

    Note
    ----
    Uses the same bit expansion that's included in SP800-22's `sts`
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
    """Container for a SP800-22 example"""

    randtest: str
    bits: List[int]
    statistic: Union[int, float]
    p: float
    kwargs: Dict[str, Any] = {}


class MultiExample(NamedTuple):
    """Container for a SP800-22 example with multiple results"""

    randtest: str
    bits: List[int]
    statistics: List[Union[int, float]]
    pvalues: List[float]
    kwargs: Dict[str, Any] = {}


class SubExample(NamedTuple):
    """Container for a single SP800-22 example of a test with multiple results"""

    randtest: str
    key: Any
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
        # FAILING scipys fft produces slightly diff transformations to SP800-22's sts
        #         TODO  - check if examples succeed using SP800-22's fourier transforming
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
        # FAILING p off by ~0.07 if gammaincc(df/2, statistic/2) and df=2
        randtest="overlapping_template_matching",

        bits=[
            1, 0, 1, 1, 1, 0, 1, 1, 1, 1,
            0, 0, 1, 0, 1, 1, 0, 1, 1, 0,  # Modifed 2nd block of SP800-22 example
            0, 1, 1, 1, 0, 0, 1, 0, 1, 1,  # originally had 1 match
            1, 0, 1, 1, 1, 1, 1, 0, 0, 0,  # now has 2 matches, as expected
            0, 1, 0, 1, 1, 0, 1, 0, 0, 1,
        ],
        kwargs={
            "template_size": 2,
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
            "template_size": 9,
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
        randtest="approximate_entropy",

        bits=[0, 1, 0, 0, 1, 1, 0, 1, 0, 1],
        kwargs={
            "blocksize": 3
        },

        statistic=10.043859999999999,  # SP800-22 erroneously had 0.502193
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
    ),
]

multi_examples = [
    MultiExample(
        # FAILING - SP800-22's result is not replicated by sts
        #         - sts result matches our own
        randtest="serial",

        bits=[0, 0, 1, 1, 0, 1, 1, 1, 0, 1],
        kwargs={
            "blocksize": 3
        },

        statistics=[1.6, 0.8],
        pvalues=[0.9057, 0.8805],
    ),
    MultiExample(
        randtest="serial",

        bits=list(e_expansion()),
        kwargs={
            "blocksize": 2
        },

        statistics=[0.339764, 0.336400],
        pvalues=[0.843764, 0.561915],
    ),
    MultiExample(
        # FAILING - SP800-22's result is not replicated by sts
        #         - sts result matches our own
        randtest="random_excursions",

        bits=list(e_expansion()),

        statistics=[
            3.835698,
            7.318707,
            7.861927,
            15.692617,
            2.485906,
            5.429381,
            2.404171,
            2.393928,
        ],
        pvalues=[
            0.573306,
            0.197996,
            0.164011,
            0.007779,
            0.778616,
            0.365752,
            0.790853,
            0.792378,
        ]
    ),
    MultiExample(
        # FAILING - SP800-22's result is not replicated by sts
        #         - sts result matches our own
        randtest="random_excursions_variant",

        bits=list(e_expansion()),

        statistics=[
            1450,
            1435,
            1380,
            1366,
            1412,
            1475,
            1480,
            1468,
            1502,
            1409,
            1369,
            1396,
            1479,
            1599,
            1628,
            1619,
            1620,
            1610,
        ],
        pvalues=[
            0.858946,
            0.794755,
            0.576249,
            0.493417,
            0.633873,
            0.917283,
            0.934708,
            0.816012,
            0.826009,
            0.137861,
            0.200642,
            0.441254,
            0.939291,
            0.505683,
            0.445935,
            0.512207,
            0.538635,
            0.593930,
        ]
    )
]

sub_examples = [
    SubExample(
        randtest="non_overlapping_template_matching",

        key=(0, 0, 1),

        bits=[
            1, 0, 1, 0, 0, 1, 0, 0,
            1, 0, 1, 1, 1, 0, 0, 1,
            0, 1, 1, 0,
        ],
        kwargs={
            "template_size": 3,
            "nblocks": 2,
        },

        statistic=2.133333,
        p=0.344154,
    ),
    SubExample(
        randtest="random_excursions",

        key=1,

        bits=[0, 1, 1, 0, 1, 1, 0, 1, 0, 1],

        statistic=4.333033,
        p=0.502529,
    ),
    SubExample(
        randtest="random_excursions_variant",

        key=1,

        bits=[0, 1, 1, 0, 1, 1, 0, 1, 0, 1],

        statistic=4,
        p=0.683091,
    ),
]
# fmt: on


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


@pytest.mark.parametrize(MultiExample._fields, multi_examples)
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_multi_examples(randtest, bits, statistics, pvalues, kwargs):
    randtest_method = getattr(randtests, randtest)

    results = randtest_method(bits, **kwargs)

    if isinstance(statistics[0], float):
        for statistic_expect, statistic in zip(statistics, results.statistics):
            assert isclose(statistic, statistic_expect, rel_tol=0.05)
    elif isinstance(statistics[0], int):
        for statistic_expect, statistic in zip(statistics, results.statistics):
            assert statistic == statistic_expect

    for p_expect, p in zip(pvalues, results.pvalues):
        assert isclose(p, p_expect, rel_tol=0.05)


@pytest.mark.parametrize(SubExample._fields, sub_examples)
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_sub_examples(randtest, key, bits, statistic, p, kwargs):
    randtest_method = getattr(randtests, randtest)

    results = randtest_method(bits, **kwargs)
    result = results[key]

    if isinstance(statistic, float):
        assert isclose(result.statistic, statistic, rel_tol=0.05)
    elif isinstance(statistic, int):
        assert result.statistic == statistic

    assert isclose(result.p, p, abs_tol=0.005)
