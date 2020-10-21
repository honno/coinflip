from pytest import mark

from coinflip import randtests

from .examples import *


@mark.parametrize(Example._fields, examples)
def test_examples(randtest, bits, statistic_expect, p_expect, kwargs):
    randtest_method = getattr(randtests, randtest)

    result = randtest_method(bits, **kwargs)

    assert_statistic(result.statistic, statistic_expect)
    assert_p(result.p, p_expect)


@mark.parametrize(MultiExample._fields, multi_examples)
def test_multi_examples(randtest, bits, expected_statistics, expected_pvalues, kwargs):
    randtest_method = getattr(randtests, randtest)

    results = randtest_method(bits, **kwargs)

    assert_statistics(results.statistics, expected_statistics)
    assert_pvalues(results.pvalues, expected_pvalues)


@mark.parametrize(SubExample._fields, sub_examples)
def test_sub_examples(randtest, key, bits, statistic_expect, p_expect, kwargs):
    randtest_method = getattr(randtests, randtest)

    results = randtest_method(bits, **kwargs)
    result = results[key]

    assert_statistic(result.statistic, statistic_expect)
    assert_p(result.p, p_expect)
