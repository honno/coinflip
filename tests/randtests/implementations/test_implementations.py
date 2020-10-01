"""Assert test results from examples on implementations

Notes
------
``testmaps`` are not directly passed to ``test_examples``, because pytest's
generated parameter names (i.e. from --collect-only) won't hold the respective
implementation names.
"""
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

testmaps = {"nist": nist_testmap, "sgr": sgr_testmap, "dj": dj_testmap}


def author_examples() -> Iterator:
    for author in testmaps.keys():
        for example in examples:
            yield (author, *example)


fields = list(Example._fields)
fields.insert(0, "author")


@pytest.mark.parametrize(fields, author_examples())
def test_examples(author, randtest, bits, statistic, p, kwargs):
    testmap = testmaps[author]
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
