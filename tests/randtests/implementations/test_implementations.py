"""Assert test results from examples on implementations"""
from math import isclose
from typing import Iterator

import pytest
from pytest import skip

from ..test_examples import Example
from ..test_examples import examples
from ._implementation import ImplementationError
from .dj import testmap as dj_testmap
from .nist import testmap as nist_testmap
from .sgr import testmap as sgr_testmap

testmaps = [nist_testmap, sgr_testmap, dj_testmap]


def testmap_examples() -> Iterator:
    for testmap in testmaps:
        for example in examples:
            yield (testmap, *example)


fields = list(Example._fields)
fields.insert(0, "testmap")


@pytest.mark.parametrize(fields, testmap_examples())
def test_examples(testmap, randtest, bits, statistic, p, kwargs):
    implementation = testmap[randtest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        result = implementation.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    if isinstance(result, float):
        assert isclose(result, p, abs_tol=0.005)
    else:
        assert isclose(result.p, p, abs_tol=0.005)
