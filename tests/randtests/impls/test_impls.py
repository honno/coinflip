from pytest import mark
from pytest import skip

from ..examples import *
from . import testmaps
from .core import ImplementationError


@mark.parametrize("author", testmaps.keys())
@mark.parametrize(example_fields, examples)
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


@mark.parametrize("author", testmaps.keys())
@mark.parametrize(multi_example_fields, multi_examples)
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
