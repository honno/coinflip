from math import isclose

from pytest import skip

from . import sgr_testmap


def test_stattest_on_example(stattest, bits, statistic, p, kwargs):
    implementation = sgr_testmap[stattest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        result = implementation.stattest(bits, **kwargs)
    except NotImplementedError:
        skip()

    assert isclose(result, p, abs_tol=0.005)
