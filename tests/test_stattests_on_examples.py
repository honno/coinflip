# fmt: off
from math import isclose
from typing import NamedTuple
from typing import Union

import pandas as pd

from rngtest.stattests import fourier
from rngtest.stattests import frequency
from rngtest.stattests import matrix
from rngtest.stattests import runs
from rngtest.stattests import template
from rngtest.stattests import universal


class StattestResult(NamedTuple):
    statistic: int
    p: Union[int, float]


def example(bits, statistic, p, stattest, **kwargs):
    def decorator(testing_function):
        def wrapper():
            series = pd.Series(bits)
            our_result = stattest(series, **kwargs)

            example_result = StattestResult(statistic=statistic, p=p)

            testing_function(our_result, example_result)

        return wrapper

    return decorator


@example(
    stattest=frequency.monobits,

    bits=[1, 0, 1, 1, 0, 1, 0, 1, 0, 1],

    statistic=.632455532,
    p=0.527089,
)
def test_monobits_small(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.05)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
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
    block_size=10,

    statistic=7.2,
    p=0.706438,
)
def test_frequency_within_block_large(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.05)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
    stattest=runs.runs,

    bits=[
        1, 0, 0, 1, 1, 0, 1, 0,
        1, 1
    ],

    statistic=7,
    p=0.147232,
)
def test_runs_small(our_result, nist_result):
    assert our_result.statistic == nist_result.statistic
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
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
)
def test_longest_runs_large(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
    stattest=matrix.binary_matrix_rank,

    bits=[
        0, 1, 0, 1, 1, 0, 0, 1,
        0, 0, 1, 0, 1, 0, 1, 0,
        1, 1, 0, 1,
    ],
    matrix_rows=3,
    matrix_cols=3,

    statistic=0.596953,
    p=0.741948,
)
def test_binary_matrix_rank_small(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
    stattest=fourier.discrete_fourier_transform,

    bits=[1, 0, 0, 1, 0, 1, 0, 0, 1, 1],

    statistic=-2.176429,
    p=0.029523,
)
def test_discrete_fourier_transform_small(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
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
)
def test_discrete_fourier_transform_large(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
    stattest=template.non_overlapping_template_matching,

    bits=[
        1, 0, 1, 0, 0, 1, 0, 0,
        1, 0, 1, 1, 1, 0, 0, 1,
        0, 1, 1, 0
    ],
    template=pd.Series([0, 0, 1]),
    nblocks=2,

    statistic=2.133333,
    p=0.344154,
)
def test_non_overlapping_template_matching_small(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
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
    template=pd.Series([1, 1]),
    nblocks=5,

    statistic=3.167729,
    p=0.274932,
)
def test_overlapping_template_matching_small(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


@example(
    stattest=universal.maurers_universal,

    bits=[
        0, 1, 0, 1, 1, 0, 1, 0,
        0, 1, 1, 1, 0, 1, 0, 1,
        0, 1, 1, 1,
    ],
    block_size=2,
    init_nblocks=4,

    statistic=1.1949875,
    p=0.767189,
)
def test_maurers_universal(our_result, nist_result):
    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)
