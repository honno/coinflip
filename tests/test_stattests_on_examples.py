# fmt: off
from math import isclose

import pandas as pd

from rngtest.stattests import frequency
from rngtest.stattests import matrix
from rngtest.stattests import runs
from rngtest.stattests.common import TestResult as _TestResult


def test_frequency_within_block():
    bits = [
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
    ]

    our_result = frequency.frequency_within_block(pd.Series(bits), block_size=10)
    nist_result = _TestResult(statistic=7.2, p=0.706438)

    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.05)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


def test_runs():
    bits = [
        1, 0, 0, 1, 1, 0, 1, 0,
        1, 1
    ]

    our_result = runs.runs(pd.Series(bits))
    nist_result = _TestResult(statistic=7, p=0.147232)

    assert isclose(our_result.statistic, nist_result.statistic)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


def test_longest_runs():
    bits = [
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
    ]

    our_result = runs.longest_runs(pd.Series(bits))
    nist_result = _TestResult(statistic=4.882605, p=0.180609)

    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)


def test_matrix_rank():
    bits = [
        0, 1, 0, 1, 1, 0, 0, 1,
        0, 0, 1, 0, 1, 0, 1, 0,
        1, 1, 0, 1,
    ]

    our_result = matrix.matrix_rank_test(
        pd.Series(bits), matrix_rows=3, matrix_cols=3
    )
    nist_result = _TestResult(statistic=0.596953, p=0.741948)

    assert isclose(our_result.statistic, nist_result.statistic, abs_tol=0.005)
    assert isclose(our_result.p, nist_result.p, abs_tol=0.005)
