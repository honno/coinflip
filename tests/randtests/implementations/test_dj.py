"""Assert test results from examples on David Johnston's sts implementation"""
from math import isclose

from pytest import skip

from . import dj_testmap


def test_randtest_on_example(randtest, bits, statistic, p, kwargs):
    implementation = dj_testmap[randtest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        result = implementation.randtest(bits, **kwargs)
    except NotImplementedError:
        skip()

    assert isclose(result.p, p, abs_tol=0.005)
