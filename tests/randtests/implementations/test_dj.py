"""Assert test results from examples on David Johnston's sts implementation"""
from collections.abc import Generator
from math import isclose

import pytest
from pytest import skip

from ...test_algorithms import bm_examples
from ._implementation import ImplementationError
from .dj import berlekamp_massey
from .dj import testmap


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

    assert isclose(result.p, p, abs_tol=0.005)


@pytest.mark.parametrize(["sequence", "min_size"], bm_examples)
def test_berlekamp_massey(sequence, min_size):
    assert berlekamp_massey(sequence) == min_size
