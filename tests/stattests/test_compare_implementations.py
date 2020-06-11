from math import isclose

import pandas as pd
from hypothesis import assume
from hypothesis import given
from hypothesis import strategies as st

from rngtest.stattests import fourier
from rngtest.stattests import frequency
from rngtest.stattests import runs

from .implementations import djmap


def contains_multiple_values(array):
    firstval = array[0]
    for val in array[1:]:
        if val != firstval:
            return True
    else:
        return False


def mixedbits(min_size=2):
    binary = st.integers(min_value=0, max_value=1)
    bits = st.lists(binary, min_size=min_size)
    mixedbits = bits.filter(contains_multiple_values)

    return mixedbits


@given(mixedbits())
def test_monobits(bits):
    ourresult = frequency.monobits(pd.Series(bits))

    djtest = djmap[frequency.monobits].stattest
    djresult = djtest(bits)

    assert isclose(ourresult.p, djresult.p, abs_tol=0.005)


@given(mixedbits(min_size=100))
def test_frequency_within_block(bits):
    dj_implementation = djmap[frequency.frequency_within_block]
    djtest = dj_implementation.stattest
    kwargs = dj_implementation.fixedkwargs

    ourresult = frequency.frequency_within_block(pd.Series(bits), **kwargs)
    djresult = djtest(bits)

    assert isclose(ourresult.p, djresult.p, abs_tol=0.005)


@given(mixedbits())
def test_runs(bits):
    ourresult = runs.runs(pd.Series(bits))

    djtest = djmap[runs.runs].stattest
    djresult = djtest(bits)

    assert isclose(ourresult.p, djresult.p)


@given(mixedbits())
def test_discrete_fourier_transform(bits):
    if len(bits) % 2 != 0:
        truncated_bits = bits[:-1]
        assume(0 in truncated_bits and 1 in truncated_bits)

    ourresult = fourier.discrete_fourier_transform(pd.Series(bits))

    djtest = djmap[fourier.discrete_fourier_transform].stattest
    djresult = djtest(bits)

    assert isclose(ourresult.p, djresult.p)
