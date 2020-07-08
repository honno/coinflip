from math import isclose

import pytest

from rngtest import randtests


# conftest.py is responsible for parametrizing, equivalent to:
# @pytest.mark.parametrize(Example._fields, examples_iter())
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_stattest_on_example(stattest, bits, statistic, p, kwargs):
    stattest_method = getattr(randtests, stattest)

    result = stattest_method(bits, **kwargs)

    if isinstance(statistic, float):
        assert isclose(result.statistic, statistic, rel_tol=0.05)
    elif isinstance(statistic, int):
        assert result.statistic == statistic

    assert isclose(result.p, p, abs_tol=0.005)
