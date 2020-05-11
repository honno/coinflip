from math import isclose

import pandas as pd
from hypothesis import given

from rngtest.stattests import frequency
from rngtest.stattests import runs

from .implementations import dj
from .implementations import steven
from .strategies import random_bits_strategy


@given(random_bits_strategy)
def test_monobits(bits):
    our_result = frequency.monobits(pd.Series(bits))
    dj_result = dj.monobit_test(bits)

    assert isclose(our_result.p, dj_result.p)


# TODO figure out sensible isclose margins for extreme sequence inputs
# @given(large_random_bits_strategy)
# def test_frequency_within_block(bits):
#     our_result = frequency.frequency_within_block(pd.Series(bits), block_size=dj.block_size)
#     dj_result = dj.frequency_within_block_test(bits)

#     assert isclose(our_result.p, dj_result.p, abs_tol=0.005)


def test_frequency_within_block_on_example():
    bits = [
        1,
        1,
        0,
        0,
        1,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        1,
        1,
        0,
        1,
        0,
        1,
        0,
        1,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        0,
        1,
        0,
        1,
        1,
        0,
        1,
        0,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        0,
        1,
        0,
        0,
        0,
        1,
        1,
        0,
        1,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        1,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        1,
        1,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        1,
        0,
        1,
        0,
        0,
        0,
        1,
        0,
        1,
        1,
        1,
        0,
        0,
        0,
    ]

    our_result = frequency.frequency_within_block(pd.Series(bits), block_size=10)
    nist_p = 0.706438

    assert isclose(our_result.p, nist_p, abs_tol=0.005)


@given(random_bits_strategy)
def test_runs(bits):
    our_result = runs.runs(pd.Series(bits))
    dj_result = dj.runs_test(bits)
    steven_result = steven.runs_test(bits)

    assert isclose(our_result.p, dj_result.p)
    assert isclose(our_result.p, steven_result.p)


def test_runs_on_example():
    bits = [1, 0, 0, 1, 1, 0, 1, 0, 1, 1]

    our_result = runs.runs(pd.Series(bits))
    nist_p = 0.147232

    assert isclose(our_result.p, nist_p, abs_tol=0.005)
