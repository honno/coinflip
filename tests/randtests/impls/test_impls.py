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
        impl = testmap[randtest]
    except KeyError:
        skip()

    for key in impl.missingkwargs:
        if key in kwargs.keys():
            skip()

    for key, value in impl.fixedkwargs.items():
        if kwargs[key] != value:
            skip()

    try:
        p = impl.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    assert_p(p, p_expect)


@mark.parametrize("author", testmaps.keys())
@mark.parametrize(multi_example_fields, multi_examples)
def test_multi_examples(
    author, randtest, bits, expected_statistics, expected_pvalues, kwargs
):
    testmap = testmaps[author]
    impl = testmap[randtest]

    for key in impl.missingkwargs:
        if key in kwargs.keys():
            skip()

    for key, value in impl.fixedkwargs.items():
        if kwargs[key] != value:
            skip()

    try:
        pvalues = impl.randtest(bits, **kwargs)
    except ImplementationError:
        skip()

    assert_pvalues(pvalues, expected_pvalues)
