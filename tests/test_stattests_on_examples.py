from math import isclose

import pandas as pd

from rngtest.stattests import frequency
from rngtest.stattests import matrix
from rngtest.stattests import runs

# fmt: off


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
    nist_p = 0.706438

    assert isclose(our_result.p, nist_p, abs_tol=0.005)


def test_runs():
    bits = [
        1, 0, 0, 1, 1, 0, 1, 0,
        1, 1
    ]

    our_result = runs.runs(pd.Series(bits))
    nist_p = 0.147232

    assert isclose(our_result.p, nist_p, abs_tol=0.005)


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
    nist_p = 0.180609

    assert isclose(our_result.p, nist_p, abs_tol=0.005)


def test_matrix_rank():
    bits = [
        0, 1, 0, 1, 1, 0, 0, 1,
        0, 0, 1, 0, 1, 0, 1, 0,
        1, 1, 0, 1,
    ]

    our_result = matrix.matrix_rank_test(
        pd.Series(bits), matrix_rows=3, matrix_cols=3
    )
    nist_p = 0.741948

    assert isclose(our_result.p, nist_p, abs_tol=0.005)
