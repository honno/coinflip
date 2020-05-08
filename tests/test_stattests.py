from math import isclose

import pandas as pd
from hypothesis import given

from rngtest.stattests import frequency
from rngtest.stattests import runs

from .implementations import dj
from .strategies import random_bits_strategy


@given(random_bits_strategy)
def test_monobits(bits):
    our_result = frequency.monobits_test(pd.Series(bits))
    dj_result = dj.monobit_test(bits)

    assert isclose(our_result.p, dj_result.p)


@given(random_bits_strategy)
def test_runs(bits):
    our_result = runs.runs(pd.Series(bits))
    dj_result = dj.runs_test(bits)

    assert isclose(our_result.p, dj_result.p)


def test_runs_on_nist():
    bits = [1, 0, 0, 1, 1, 0, 1, 0, 1, 1]

    our_result = runs.runs(pd.Series(bits))
    nist_p = 0.147232

    assert isclose(our_result.p, nist_p, abs_tol=0.005)
