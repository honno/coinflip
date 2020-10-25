import pandas as pd
from pytest import raises

from coinflip._randtests.common.testutils import slider


def test_slider():
    series = pd.Series([0, 1, 0, 0, 1])
    it = slider(series, 0)

    with raises(StopIteration):
        next(it)
