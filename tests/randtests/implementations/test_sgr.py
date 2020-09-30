"""Assert test results from examples on r4nd0m"""
from math import isclose

import pytest
from pytest import skip

from ...test_algorithms import bm_examples
from ._implementation import ImplementationError
from .sgr import berlekamp_massey
from .sgr import testmap


def test_randtest_on_example(randtest, bits, statistic, p, kwargs):
    implementation = testmap[randtest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        result = implementation.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    assert isclose(result, p, abs_tol=0.005)


@pytest.mark.parametrize(["sequence", "min_size"], bm_examples)
def test_berlekamp_massey(sequence, min_size):
    assert berlekamp_massey(sequence) == min_size
