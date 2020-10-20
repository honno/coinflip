from math import isclose

from pytest import mark

from coinflip import refimpl

from .test_examples import examples
from .test_examples import multi_examples

example_fields = ["randtest", "bits", "statistic_expect", "p_expect", "kwargs"]


@mark.parametrize(example_fields, examples)
def test_examples(randtest, bits, statistic_expect, p_expect, kwargs):
    randtest_method = getattr(refimpl, randtest)

    statistic, p = randtest_method(bits, **kwargs)

    if isinstance(statistic, int):
        assert statistic == statistic_expect
    else:
        assert isclose(statistic, statistic_expect, rel_tol=0.05)

    assert isclose(p, p_expect, abs_tol=0.005)


multi_fields = ["randtest", "bits", "expected_statistics", "expected_pvalues", "kwargs"]


@mark.parametrize(multi_fields, multi_examples)
def test_multi_examples(randtest, bits, expected_statistics, expected_pvalues, kwargs):
    randtest_method = getattr(refimpl, randtest)

    statistics, pvalues = randtest_method(bits, **kwargs)

    for statistic, statistic_expect in zip(statistics, expected_statistics):
        if isinstance(statistic, int):
            assert statistic == statistic_expect
        else:
            assert isclose(statistic, statistic_expect, rel_tol=0.05)

    for p, p_expect in zip(pvalues, expected_pvalues):
        assert isclose(p, p_expect, rel_tol=0.05)
