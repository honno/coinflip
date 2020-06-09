from math import isclose
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Union

import pandas as pd
import pytest

from rngtest.stattests import complexity
from rngtest.stattests import fourier
from rngtest.stattests import frequency
from rngtest.stattests import matrix
from rngtest.stattests import runs
from rngtest.stattests import template
from rngtest.stattests import universal

tests_path = Path(__file__).parent
data_path = tests_path / "data"


def e_expansion():
    with open(data_path / "e_expansion.txt") as f:
        for line in f:
            for x in line:
                if x == "0" or x == "1":
                    bit = int(x)

                    yield bit


class Example(NamedTuple):
    stattest: Callable
    bits: List[int]
    statistic: Union[int, float]
    p: float
    kwargs: Dict[str, Any] = dict()


# fmt: off
examples = [
    Example(
        stattest=frequency.monobits,

        bits=[1, 0, 1, 1, 0, 1, 0, 1, 0, 1],

        statistic=.632455532,
        p=0.527089,
    ),
    Example(
        stattest=frequency.monobits,

        bits=[1, 0, 1, 1, 0, 1, 0, 1, 0, 1],

        statistic=.632455532,
        p=0.527089,
    ),
    Example(
        stattest=frequency.frequency_within_block,

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
        kwargs={"blocksize": 10},

        statistic=7.2,
        p=0.706438,
    ),
    Example(
        stattest=runs.runs,

        bits=[
            1, 0, 0, 1, 1, 0, 1, 0,
            1, 1
        ],

        statistic=7,
        p=0.147232,
    ),
    Example(
        stattest=runs.longest_runs,

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
        stattest=matrix.binary_matrix_rank,

        bits=[
            0, 1, 0, 1, 1, 0, 0, 1,
            0, 0, 1, 0, 1, 0, 1, 0,
            1, 1, 0, 1,
        ],
        kwargs={
            "nrows": 3,
            "ncols": 3,
        },

        statistic=0.596953,
        p=0.741948,
    ),
    Example(
        stattest=fourier.discrete_fourier_transform,

        bits=[1, 0, 0, 1, 0, 1, 0, 0, 1, 1],

        statistic=-2.176429,
        p=0.029523,
    ),
    Example(
        stattest=fourier.discrete_fourier_transform,

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
        stattest=template.non_overlapping_template_matching,

        bits=[
            1, 0, 1, 0, 0, 1, 0, 0,
            1, 0, 1, 1, 1, 0, 0, 1,
            0, 1, 1, 0
        ],
        kwargs={
            "template": pd.Series([0, 0, 1]),
            "nblocks": 2,
        },

        statistic=2.133333,
        p=0.344154,
    ),
    Example(
        stattest=template.overlapping_template_matching,

        bits=[
            1, 0, 1, 1, 1, 0, 1, 1,
            1, 1, 0, 0, 1, 0, 1, 1,
            0, 1, 0, 0, 0, 1, 1, 1,
            0, 0, 1, 0, 1, 1, 1, 0,
            1, 1, 1, 1, 1, 0, 0, 0,
            0, 1, 0, 1, 1, 0, 1, 0,
            0, 1,
        ],
        kwargs={
            "template": pd.Series([1, 1]),
            "nblocks": 5,
        },

        statistic=3.167729,
        p=0.274932,
    ),
    Example(
        stattest=universal.maurers_universal,

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
        stattest=complexity.linear_complexity,

        bits=e_expansion(),
        kwargs={"blocksize": 1000},

        statistic=2.700348,
        p=0.845406,
    ),
]
# fmt: on


@pytest.mark.parametrize("stattest, bits, statistic, p, kwargs", examples)
def test_stattest_on_example(stattest, bits, statistic, p, kwargs):
    series = pd.Series(bits)
    result = stattest(series, **kwargs)

    if isinstance(statistic, float):
        assert isclose(result.statistic, statistic, rel_tol=0.05)
    elif isinstance(statistic, int):
        assert result.statistic == statistic

    assert isclose(result.p, p, abs_tol=0.005)
