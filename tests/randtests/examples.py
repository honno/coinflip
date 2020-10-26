"""Assert test results from examples on our implementations"""
from math import isclose
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import NamedTuple
from typing import Tuple
from typing import Union

from pytest import mark
from pytest import param
from typing_extensions import Literal

__all__ = [
    "example_fields",
    "multi_example_fields",
    "sub_example_fields",
    "examples",
    "multi_examples",
    "sub_examples",
    "assert_statistic",
    "assert_p",
    "assert_statistics",
    "assert_pvalues",
]

e_path = Path(__file__).parent / "e_expansion.txt"


def e_expansion(n=1000000) -> Iterator[int]:
    """Generates bits of e

    Note
    ----
    Uses the same bit expansion that's included in SP800-22's `sts`
    """

    def genbits():
        with open(e_path) as f:
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
    bits: List[Literal[0, 1]]
    statistic_expect: Union[int, float]
    p_expect: float
    kwargs: Dict[str, Any] = {}
    xfail: bool = False


class MultiExample(NamedTuple):
    """Container for a SP800-22 example with multiple results"""

    randtest: str
    bits: List[Literal[0, 1]]
    expected_statistics: List[Union[int, float]]
    expected_pvalues: List[float]
    kwargs: Dict[str, Any] = {}
    xfail: bool = False


class SubExample(NamedTuple):
    """Container for a single SP800-22 example of a test with multiple results"""

    randtest: str
    key: Any
    bits: List[Literal[0, 1]]
    statistic_expect: Union[int, float]
    p_expect: float
    kwargs: Dict[str, Any] = {}
    xfail: bool = False


example_fields = ["randtest", "bits", "statistic_expect", "p_expect", "kwargs"]
multi_example_fields = [
    "randtest",
    "bits",
    "expected_statistics",
    "expected_pvalues",
    "kwargs",
]
sub_example_fields = [
    "randtest",
    "key",
    "bits",
    "statistic_expect",
    "p_expect",
    "kwargs",
]


# fmt: off
_examples = [
    Example(
        randtest="monobit",

        bits=[1, 0, 1, 1, 0, 1, 0, 1, 0, 1],

        statistic_expect=.632455532,
        p_expect=0.527089,
    ),
    Example(
        randtest="monobit",

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
        statistic_expect=1.6,
        p_expect=0.109599,
    ),
    Example(
        randtest="frequency_within_block",

        bits=[
            1, 1, 0, 0, 1, 0, 0, 1, 0, 0,
            0, 0, 1, 1, 1, 1, 1, 1, 0, 1,
            1, 0, 1, 0, 1, 0, 1, 0, 0, 0,
            1, 0, 0, 0, 1, 0, 0, 0, 0, 1,
            0, 1, 1, 0, 1, 0, 0, 0, 1, 1,
            0, 0, 0, 0, 1, 0, 0, 0, 1, 1,
            0, 1, 0, 0, 1, 1, 0, 0, 0, 1,
            0, 0, 1, 1, 0, 0, 0, 1, 1, 0,
            0, 1, 1, 0, 0, 0, 1, 0, 1, 0,
            0, 0, 1, 0, 1, 1, 1, 0, 0, 0,
        ],
        kwargs={
            "blocksize": 10
        },

        statistic_expect=7.2,
        p_expect=0.706438,
    ),
    Example(
        randtest="runs",

        bits=[
            1, 0, 0, 1, 1, 0, 1, 0,
            1, 1
        ],

        statistic_expect=7,
        p_expect=0.147232,
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


        statistic_expect=4.882605,
        p_expect=0.180609,
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

        statistic_expect=0.596953,
        p_expect=0.741948,
    ),
    Example(
        randtest="binary_matrix_rank",

        bits=list(e_expansion(n=100000)),
        kwargs={
            "matrix_dimen": (32, 32),
        },

        statistic_expect=1.2619656,
        p_expect=0.532069,
    ),
    Example(
        # FAILING scipys fft produces slightly diff transformations to SP800-22's sts
        #         TODO  - check if examples succeed using SP800-22's fourier transforming
        #               - performance metrics on both solutions
        randtest="spectral",

        bits=[1, 0, 0, 1, 0, 1, 0, 0, 1, 1],

        statistic_expect=-2.176429,
        p_expect=0.029523,

        xfail=True,
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

        statistic_expect=-1.376494,
        p_expect=0.168669,

        xfail=True,
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
            "blocksize": 10,  # nblocks=5
            "df": 2,
        },

        statistic_expect=3.167729,
        p_expect=0.274932,

        xfail=True
    ),
    Example(
        randtest="overlapping_template_matching",

        bits=list(e_expansion()),
        kwargs={
            "template_size": 9,
            "blocksize": 1032,  # nblocks=968
        },

        statistic_expect=8.965859,
        p_expect=0.110434
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

        statistic_expect=1.1949875,
        p_expect=0.767189,
    ),
    Example(
        randtest="linear_complexity",

        bits=list(e_expansion()),
        kwargs={
            "blocksize": 1000
        },

        statistic_expect=2.700348,
        p_expect=0.845406,
    ),
    Example(
        randtest="approximate_entropy",

        bits=[0, 1, 0, 0, 1, 1, 0, 1, 0, 1],
        kwargs={
            "blocksize": 3
        },

        statistic_expect=10.043859999999999,  # SP800-22 erroneously had 0.502193
        p_expect=0.261961,
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

        statistic_expect=5.550792,
        p_expect=0.235301,
    ),
    Example(
        randtest="cusum",

        bits=[1, 0, 1, 1, 0, 1, 0, 1, 1, 1],

        statistic_expect=4,
        p_expect=0.4116588,
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

        statistic_expect=16,
        p_expect=0.219194,
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

        statistic_expect=19,
        p_expect=0.114866,
    ),
]

_multi_examples = [
    MultiExample(
        # FAILING - SP800-22's result is not replicated by sts
        #         - sts and dj result matches our own
        randtest="serial",

        bits=[0, 0, 1, 1, 0, 1, 1, 1, 0, 1],
        kwargs={
            "blocksize": 3
        },

        expected_statistics=[1.6, 0.8],
        expected_pvalues=[0.9057, 0.8805],

        xfail=True
    ),
    MultiExample(
        randtest="serial",

        bits=list(e_expansion()),
        kwargs={
            "blocksize": 2
        },

        expected_statistics=[0.339764, 0.336400],
        expected_pvalues=[0.843764, 0.561915],
    ),
    MultiExample(
        # FAILING - SP800-22's result is not replicated by sts
        #         - sts result matches our own
        #         - dj near to our own
        randtest="random_excursions",

        bits=list(e_expansion()),

        expected_statistics=[
            3.835698,
            7.318707,
            7.861927,
            15.692617,
            2.485906,
            5.429381,
            2.404171,
            2.393928,
        ],
        expected_pvalues=[
            0.573306,
            0.197996,
            0.164011,
            0.007779,
            0.778616,
            0.365752,
            0.790853,
            0.792378,
        ],

        xfail=True
    ),
    MultiExample(
        randtest="random_excursions_variant",

        bits=list(e_expansion()),

        expected_statistics=[
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
        expected_pvalues=[
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

_sub_examples = [
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
            "blocksize": 10,  # nblocks=2
        },

        statistic_expect=2.133333,
        p_expect=0.344154,
    ),
    SubExample(
        randtest="random_excursions",

        key=1,

        bits=[0, 1, 1, 0, 1, 1, 0, 1, 0, 1],

        statistic_expect=4.333033,
        p_expect=0.502529,
    ),
    SubExample(
        randtest="random_excursions_variant",

        key=1,

        bits=[0, 1, 1, 0, 1, 1, 0, 1, 0, 1],

        statistic_expect=4,
        p_expect=0.683091,
    ),
]
# fmt: on


# TODO make a type hint for all examples e.g. BaseExample
def wrap_examples(examples_list: List) -> List[Union[Tuple, "ParameterSet"]]:  # noqa
    argvalues = []
    for example in examples_list:
        *_argvalue, xfail = example
        marks = []
        if len(example.bits) > 1000:
            marks.append(mark.slow)
        if xfail:
            marks.append(mark.xfail)

        if marks:
            argvalue = param(*_argvalue, marks=marks)
        else:
            argvalue = _argvalue

        argvalues.append(argvalue)

    return argvalues


examples = wrap_examples(_examples)
multi_examples = wrap_examples(_multi_examples)
sub_examples = wrap_examples(_sub_examples)


def assert_statistic(statistic, statistic_expect):
    if isinstance(statistic, int):
        assert (
            statistic == statistic_expect
        ), f"statistic {statistic} != {statistic_expect}"
    else:
        assert isclose(
            statistic, statistic_expect, rel_tol=0.05
        ), f"statistic {round(statistic, 1)} != {round(statistic_expect, 1)}"


def assert_p(p, p_expect):
    assert isclose(
        p, p_expect, abs_tol=0.005
    ), f"p-value {round(p, 3)} !≈ {round(p_expect, 3)}"


def assert_statistics(statistics, expected_statistics):
    for statistic, statistic_expect in zip(statistics, expected_statistics):
        assert_statistic(statistic, statistic_expect)


def assert_pvalues(pvalues, expected_pvalues):
    for p, p_expect in zip(pvalues, expected_pvalues):
        assert_p(p, p_expect)
