from collections.abc import Mapping
from copy import copy
from math import isclose
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Union

import pytest

from rngtest import stattests

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
    stattest: str
    bits: List[int]
    statistic: Union[int, float]
    p: float
    kwargs: Dict[str, Any] = dict()


# fmt: off
examples = {
    "monobits": Example(
        stattest="monobits",

        bits=[1, 0, 1, 1, 0, 1, 0, 1, 0, 1],

        statistic=.632455532,
        p=0.527089,
    ),
    "frequency_within_block": Example(
        stattest="frequency_within_block",

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
        kwargs=dict(
            blocksize=10
        ),

        statistic=7.2,
        p=0.706438,
    ),
    "runs": Example(
        stattest="runs",

        bits=[
            1, 0, 0, 1, 1, 0, 1, 0,
            1, 1
        ],

        statistic=7,
        p=0.147232,
    ),
    "longest_runs": Example(
        stattest="longest_runs",

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
    "binary_matrix_rank": Example(
        stattest="binary_matrix_rank",

        bits=[
            0, 1, 0, 1, 1, 0, 0, 1,
            0, 0, 1, 0, 1, 0, 1, 0,
            1, 1, 0, 1,
        ],
        kwargs=dict(
            matrix_dimen=(3, 3),
        ),

        statistic=0.596953,
        p=0.741948,
    ),
    "discrete_fourier_transform": {
        "small": Example(
            stattest="discrete_fourier_transform",

            bits=[1, 0, 0, 1, 0, 1, 0, 0, 1, 1],

            statistic=-2.176429,
            p=0.029523,
        ),
        "large": Example(
            stattest="discrete_fourier_transform",

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
    },
    "non_overlapping_template_matching": Example(
        stattest="non_overlapping_template_matching",

        bits=[
            1, 0, 1, 0, 0, 1, 0, 0,
            1, 0, 1, 1, 1, 0, 0, 1,
            0, 1, 1, 0
        ],
        kwargs=dict(
            template=[0, 0, 1],
            nblocks=2,
        ),

        statistic=2.133333,
        p=0.344154,
    ),
    "overlapping_template_matching": {
        "small": Example(
            # FAILING Generated probabilities coded to something different then what we got
            stattest="overlapping_template_matching",

            bits=[
                1, 0, 1, 1, 1, 0, 1, 1,
                1, 1, 0, 0, 1, 0, 1, 1,
                0, 1, 0, 0, 0, 1, 1, 1,
                0, 0, 1, 0, 1, 1, 1, 0,
                1, 1, 1, 1, 1, 0, 0, 0,
                0, 1, 0, 1, 1, 0, 1, 0,
                0, 1,
            ],
            kwargs=dict(
                template=[1, 1],
                nblocks=5,
                df=2,
            ),

            statistic=3.167729,
            p=0.274932,
        ),
        "large": Example(
            # FAILING Getting different tallies
            stattest="overlapping_template_matching",

            bits=e_expansion(),
            kwargs=dict(
                template=[1, 1, 1, 1, 1, 1, 1, 1, 1],
                nblocks=968,
            ),

            statistic=8.965859,
            p=0.110434
        )
    },
    "maurers_universal": Example(
        stattest="maurers_universal",

        bits=[
            0, 1, 0, 1, 1, 0, 1, 0,
            0, 1, 1, 1, 0, 1, 0, 1,
            0, 1, 1, 1,
        ],
        kwargs=dict(
            blocksize=2,
            init_nblocks=4,
        ),

        statistic=1.1949875,
        p=0.767189,
    ),
    "linear_complexity": Example(
        stattest="linear_complexity",

        bits=e_expansion(),
        kwargs=dict(
            blocksize=1000
        ),

        statistic=2.700348,
        p=0.845406,
    ),
}
# fmt: on


def flatten_examples(map_, parentkeys=[]):
    for key, value in map_.items():
        keys = copy(parentkeys)
        keys.append(key)

        if isinstance(value, Mapping):
            yield from flatten_examples(value, parentkeys=keys)

        elif isinstance(value, Example):
            exampletitle = ".".join(keys)
            yield exampletitle, value


def examples_iter(title_substr: str = None):
    if title_substr is None:
        for exampletitle, example in flatten_examples(examples):
            yield example

    else:
        for exampletitle, example in flatten_examples(examples):
            if title_substr in exampletitle:
                yield example


# conftest.py is responsible for parametrizing, equivalent to:
# @pytest.mark.parametrize(Example._fields, examples_iter())
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_stattest_on_example(stattest, bits, statistic, p, kwargs):
    stattest_method = getattr(stattests, stattest)

    result = stattest_method(bits, **kwargs)

    if isinstance(statistic, float):
        assert isclose(result.statistic, statistic, rel_tol=0.05)
    elif isinstance(statistic, int):
        assert result.statistic == statistic

    assert isclose(result.p, p, abs_tol=0.005)
