from pytest import mark

from coinflip import refimpl

from .examples import *


@mark.parametrize(example_fields, examples)
def test_examples(randtest, bits, statistic_expect, p_expect, kwargs):
    randtest_method = getattr(refimpl, randtest)

    statistic, p = randtest_method(bits, **kwargs)

    assert_statistic(statistic, statistic_expect)
    assert_p(p, p_expect)


@mark.parametrize(multi_example_fields, multi_examples)
def test_multi_examples(randtest, bits, expected_statistics, expected_pvalues, kwargs):
    randtest_method = getattr(refimpl, randtest)

    statistics, pvalues = randtest_method(bits, **kwargs)

    assert_statistics(statistics, expected_statistics)
    assert_pvalues(pvalues, expected_pvalues)
