from math import isclose

import pandas as pd

from rngtest.stattests import frequency

from .implementations import dj


def test_nist_example():
    sequence = [1, 0, 1, 1, 0, 1, 0, 1, 0, 1]

    our_result = frequency.frequency(pd.Series(sequence))
    dj_result = dj.monobit_test(sequence)

    assert isclose(our_result.p, dj_result.p)
