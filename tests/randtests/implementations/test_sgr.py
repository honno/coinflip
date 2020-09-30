"""Assert test results from examples on r4nd0m"""
from math import isclose

from pytest import skip

from ._implementation import ImplementationError
from .sgr import testmap
from .sgr import berlekamp_massey


def test_randtest_on_example(randtest, bits, statistic, p, kwargs):
    implementation = testmap[randtest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        result = implementation.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    assert isclose(result, p, abs_tol=0.005)
