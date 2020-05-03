from math import isclose

import pandas as pd
from hypothesis import given
from hypothesis import strategies as st

from rngtest.stattests import frequency

from .implementations import dj


def contains_multiple_values(array):
    first_value = array[0]
    for value in array[1:]:
        if value != first_value:
            return True
    else:
        return False


@given(
    st.lists(st.integers(min_value=0, max_value=1), min_size=2).filter(
        contains_multiple_values
    )
)
def test_nist_example(bits):
    our_result = frequency.frequency(pd.Series(bits))
    dj_result = dj.monobit_test(bits)

    assert isclose(our_result.p, dj_result.p)
