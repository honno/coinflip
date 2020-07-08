from math import isclose

from pytest import skip

from . import sgr_testmap


def test_randtest_on_example(randtest, bits, statistic, p, kwargs):
    implementation = sgr_testmap[randtest]

    if implementation.missingkwargs or implementation.fixedkwargs:
        skip()

    try:
        result = implementation.randtest(bits, **kwargs)
    except NotImplementedError:
        skip()

    assert isclose(result, p, abs_tol=0.005)
