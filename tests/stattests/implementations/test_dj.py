# fmt: off
from math import isclose

from . import dj


def test_discrete_fourier_transform_small():
    bits = [1, 0, 0, 1, 0, 1, 0, 0, 1, 1]

    dj_result = dj.fourier_test(bits)
    nist_p = 0.029523

    assert isclose(dj_result.p, nist_p, abs_tol=0.005)


def test_discrete_fourier_transform_large():
    bits = [
        1, 1, 0, 0, 1, 0, 0, 1,
        0, 0, 0, 0, 1, 1, 1, 1,
        1, 1, 0, 1, 1, 0, 1, 0,
        1, 0, 1, 0, 0, 0, 1, 0,
        0, 0, 1, 0, 0, 0, 0, 1,
        0, 1, 1, 0, 1, 0, 0, 0,
        1, 1, 0, 0, 0, 0, 1, 0,
        0, 0, 1, 1, 0, 1, 0, 0,
        1, 1, 0, 0, 0, 1, 0, 0,
        1, 1, 0, 0, 0, 1, 1, 0,
        0, 1, 1, 0, 0, 0, 1, 0,
        1, 0, 0, 0, 1, 0, 1, 1,
        1, 0, 0, 0,
    ]

    dj_result = dj.fourier_test(bits)
    nist_p = 0.168669

    assert isclose(dj_result.p, nist_p, abs_tol=0.005)
