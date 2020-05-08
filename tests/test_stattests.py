from math import isclose

import pandas as pd
from hypothesis import given

from rngtest.stattests import frequency

from .implementations import dj
from .strategies import random_bits_strategy


@given(random_bits_strategy)
def test_monobits(bits):
    our_result = frequency.monobits_test(pd.Series(bits))
    dj_result = dj.monobit_test(bits)

    assert isclose(our_result.p, dj_result.p)
