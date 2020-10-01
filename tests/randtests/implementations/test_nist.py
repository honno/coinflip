"""Assert test results from examples on NIST's sts"""
from collections.abc import Generator
from math import isclose

from pytest import skip

from ._implementation import ImplementationError
from .nist import testmap


def test_randtest_on_example(randtest, bits, statistic, p, kwargs):
    implementation = testmap[randtest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    if isinstance(bits, Generator):
        bits = list(bits)

    try:
        result = implementation.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    assert isclose(result, p, abs_tol=0.005)
