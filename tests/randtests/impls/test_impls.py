"""Assert test results from examples on implementations

Notes
------
``testmaps`` are not directly passed to ``test_examples``, because pytest's
generated parameter names (i.e. from --collect-only) won't hold the respective
implementation names.
"""
from math import isclose
from typing import Iterator

from pytest import mark
from pytest import skip

from ..test_examples import Example
from ..test_examples import MultiExample
from ..test_examples import examples
from ..test_examples import multi_examples
from . import testmaps
from .core import ImplementationError


def author_examples() -> Iterator:
    for author in testmaps.keys():
        for example in examples:
            yield (author, *example)


fields = list(Example._fields)
fields.insert(0, "author")


@mark.parametrize(fields, author_examples())
def test_examples(author, randtest, bits, statistic, p, kwargs):
    testmap = testmaps[author]

    try:
        implementation = testmap[randtest]
    except KeyError:
        skip()

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        result = implementation.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    assert isclose(result, p, abs_tol=0.005)


def author_multi_examples() -> Iterator:
    for author in testmaps.keys():
        for multi_example in multi_examples:
            yield (author, *multi_example)


multi_fields = list(MultiExample._fields)
multi_fields.insert(0, "author")


@mark.parametrize(multi_fields, author_multi_examples())
def test_multi_examples(author, randtest, bits, statistics, pvalues, kwargs):
    testmap = testmaps[author]
    implementation = testmap[randtest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        results = implementation.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    for p_expect, p in zip(pvalues, results):
        assert isclose(p, p_expect, rel_tol=0.05)
