from math import isclose

from pytest import skip

from .dj import testmap


def test_stattest_on_example(stattest, bits, statistic, p, kwargs):
    if kwargs:
        skip()
    else:
        implementation = testmap[stattest]
        result = implementation.stattest(bits)

        assert isclose(result.p, p, abs_tol=0.005)
