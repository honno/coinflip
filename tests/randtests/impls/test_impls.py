"""Assert test results from examples on implementations

Notes
------
``testmaps`` are not directly passed to ``test_examples``, because pytest's
generated parameter names (i.e. from --collect-only) won't hold the respective
implementation names.
"""
from typing import Iterator

from pytest import mark
from pytest import skip

from ..examples import *
from . import testmaps
from .core import ImplementationError


def author_examples() -> Iterator:
    for author in testmaps.keys():
        for example in examples:
            yield (author, *example)


fields = list(example_fields)
fields.insert(0, "author")


@mark.parametrize(fields, author_examples())
def test_examples(author, randtest, bits, statistic_expect, p_expect, kwargs):
    testmap = testmaps[author]

    try:
        implementation = testmap[randtest]
    except KeyError:
        skip()

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        p = implementation.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    assert_p(p, p_expect)


def author_multi_examples() -> Iterator:
    for author in testmaps.keys():
        for multi_example in multi_examples:
            yield (author, *multi_example)


multi_fields = list(multi_example_fields)
multi_fields.insert(0, "author")


@mark.parametrize(multi_fields, author_multi_examples())
def test_multi_examples(
    author, randtest, bits, expected_statistics, expected_pvalues, kwargs
):
    testmap = testmaps[author]
    implementation = testmap[randtest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        pvalues = implementation.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    assert_pvalues(pvalues, expected_pvalues)
