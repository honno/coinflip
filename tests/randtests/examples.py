"""Defines result examples to run on randomness tests

`SP800-22 <https://github.com/Honno/coinflip/blob/master/SP800-22.pdf>`_
graciously provides examples to their tests, which are programmatically outlined
as `Example` named tuples in this module.

They are bundled in the nested dictionary `examples`, grouped by the test they
correspond and other relevant features.

`examples_iter` iterates all examples present in the dictionary, to assert
randomness tests with the same parameters result in the same result. It also
allows for filtering via a `regex` keyword argument.

Notes
-----
All examples are made in conjuction with the test specifications in section 2.,
"Random Number Generation Tests", p. 23-62.
"""
import re
from collections.abc import Mapping
from copy import copy
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import NamedTuple
from typing import Tuple
from typing import Union

tests_path = Path(__file__).parent
data_path = tests_path / "data"


__all__ = ["examples_iter"]


def _e_expansion():
    with open(data_path / "e_expansion.txt") as f:
        for line in f:
            for x in line:
                if x == "0" or x == "1":
                    bit = int(x)

                    yield bit


def e_expansion(n=1000000) -> Iterator[int]:
    """Generates bits of e

    Note
    ----
    Uses the same bit expansion that's included in NIST's `sts`
    """
    e = _e_expansion()
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
examples = {
    "monobit": Example(
        randtest="monobit",

        bits=[1, 0, 1, 1, 0, 1, 0, 1, 0, 1],

        statistic=.632455532,
        p=0.527089,
    ),
    "frequency_within_block": Example(
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
    "runs": Example(
        randtest="runs",

        bits=[
            1, 0, 0, 1, 1, 0, 1, 0,
            1, 1
        ],

        statistic=7,
        p=0.147232,
    ),
    "longest_runs": Example(
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
    "binary_matrix_rank": {
        "small": Example(
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
        "large": Example(
            randtest="binary_matrix_rank",

            bits=e_expansion(n=100000),
            kwargs={
                "matrix_dimen": (32, 32),
            },

            statistic=1.2619656,
            p=0.532069,
        )
    },
    "spectral": {
        # FAILING scipys fft produces slightly diff transformations to NIST's sts
        #         TODO  - check if examples succeed using NIST's fourier transforming
        #               - performance metrics on both solutions
        "small": Example(
            randtest="spectral",

            bits=[1, 0, 0, 1, 0, 1, 0, 0, 1, 1],

            statistic=-2.176429,
            p=0.029523,
        ),
        "large": Example(
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
    },
    "non_overlapping_template_matching": Example(
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
    "overlapping_template_matching": {
        "small": Example(
            # FAILING p off by ~0.07 if gammaincc(df/2, statistic/2) and df=2
            randtest="overlapping_template_matching",

            bits=[
                1, 0, 1, 1, 1, 0, 1, 1, 1, 1,
                0, 0, 1, 0, 1, 1, 0, 1, 1, 0,  # Modifed block 2 of NIST example
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
        "large": Example(
            # FAILING Getting different tallies
            randtest="overlapping_template_matching",

            bits=e_expansion(),
            kwargs={
                "template": [1, 1, 1, 1, 1, 1, 1, 1, 1],
                "nblocks": 968,
            },

            statistic=8.965859,
            p=0.110434
        )
    },
    "maurers_universal": Example(
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
    "linear_complexity": Example(
        randtest="linear_complexity",

        bits=e_expansion(),
        kwargs={
            "blocksize": 1000
        },

        statistic=2.700348,
        p=0.845406,
    ),
    "approximate_entropy": {
        "small": Example(
            randtest="approximate_entropy",

            bits=[0, 1, 0, 0, 1, 1, 0, 1, 0, 1],
            kwargs={
                "blocksize": 3
            },

            statistic=0.502193,
            p=0.261961,
        ),
        "large": Example(
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
    }
}
# fmt: on


def flatten_examples(
    map_: Mapping, parentkeys: List[str] = []
) -> Iterator[Tuple[str, Example]]:
    """Generates flat list of the `examples` tree

    Each example is paired with a title. The title is a dot-delimited
    concatenation of the example's parent keys.
    """
    for key, value in map_.items():
        keys = copy(parentkeys)
        keys.append(key)

        if isinstance(value, Mapping):
            yield from flatten_examples(value, parentkeys=keys)

        elif isinstance(value, Example):
            example_title = ".".join(keys)
            yield example_title, value


def examples_iter(regex: str = ".*") -> Iterator[Example]:
    """Generates examples, filtered with regex

    The regex expression is matched to the titles of the examples.

    See Also
    --------
    flatten_examples : Method used to flatten the `examples` tree
    """
    regexc = re.compile(regex)

    for example_title, example in flatten_examples(examples):
        if regexc.match(example_title):
            yield example
