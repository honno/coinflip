from math import isclose

import pandas as pd
from hypothesis import given

from rngtest.stattests import frequency

from .implementations import dj
from .strategies import random_bits_strategy


@given(random_bits_strategy)
def test_nist_example(bits):
    our_result = frequency.frequency(pd.Series(bits))
    dj_result = dj.monobit_test(bits)

    assert isclose(our_result.p, dj_result.p)
