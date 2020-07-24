"""Compares results of our tests to those of other implementations"""
from math import floor
from math import log
from math import sqrt
from typing import Tuple

import pandas as pd
from hypothesis import HealthCheck
from hypothesis import assume
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

import coinflip.randtests as randtests

from .implementations._implementation import ImplementationError
from .implementations.dj import testmap as dj_testmap
from .implementations.sgr import testmap as sgr_testmap
from .strategies import mixedbits


def pclose(p1: float, p2: float) -> bool:
    """Finds if two p-values are reasonably close to each other

    Small p-values tend to vary widely accross implementations, and so the
    closeness margin is more lenient the closer the p-values are to 0."""
    p_avg = (p1 + p2) / 2
    margin = max(-log(p_avg), 0.05)
    diff = abs(p1 - p2)

    return diff < margin


# ------------------------------------------------------------------------------
# Strategy definition


@st.composite
def blocks_strategy(draw, min_size=2) -> SearchStrategy[Tuple[int, int]]:
    bits = draw(mixedbits(min_size=min_size))

    n = len(bits)

    blocksize = draw(st.integers(min_value=1, max_value=n))

    return bits, blocksize


@st.composite
def matrix_strategy(
    draw, min_blocks=1, square_matrix=False
) -> SearchStrategy[Tuple[int, Tuple[int, int]]]:
    nblocks = draw(st.integers(min_value=min_blocks))

    if square_matrix:
        nrows = floor(sqrt(nblocks))
        ncols = nrows
    else:
        nrows = draw(st.integers(min_value=1, max_value=nblocks // 2))
        ncols = draw(st.integers(min_value=2, max_value=max(nrows, 2)))

    blocksize = nrows * ncols
    n = nblocks * blocksize
    bits = draw(mixedbits(min_size=n))

    matrix_dimen = (nrows, ncols)

    return bits, matrix_dimen


@st.composite
def template_strategy(draw, template, nblocks) -> SearchStrategy[int]:
    templatesize = len(template)
    n = nblocks * templatesize

    bits = draw(mixedbits(min_size=n))

    return bits


@st.composite
def universal_strategy(
    draw, min_blocks=2, blocksize_max=16
) -> SearchStrategy[Tuple[int, int, int]]:
    nblocks = draw(st.integers(min_value=min_blocks))

    blocksize = draw(st.integers(min_value=2, max_value=blocksize_max))

    init_nblocks = draw(st.integers(min_value=1, max_value=nblocks - 1))

    n = nblocks * blocksize
    bits = draw(mixedbits(min_size=n))

    return bits, blocksize, init_nblocks


# ------------------------------------------------------------------------------
# Property testing


@given(mixedbits())
def test_monobits(bits):
    result = randtests.monobits(pd.Series(bits))

    dj_randtest = dj_testmap["monobits"].randtest
    dj_result = dj_randtest(bits)

    assert pclose(result.p, dj_result.p)

    sgr_randtest = sgr_testmap["monobits"].randtest
    sgr_p = sgr_randtest(bits)

    assert pclose(result.p, sgr_p)


@given(mixedbits(min_size=100))
def test_dj_frequency_within_block(bits):
    _implementation = dj_testmap["frequency_within_block"]
    dj_randtest = _implementation.randtest
    dj_fixedkwargs = _implementation.fixedkwargs

    result = randtests.frequency_within_block(pd.Series(bits), **dj_fixedkwargs)
    dj_result = dj_randtest(bits)

    assert pclose(result.p, dj_result.p)


@given(blocks_strategy(min_size=100))
def test_sgr_frequency_within_block(args):
    bits, blocksize = args

    result = randtests.frequency_within_block(bits, blocksize=blocksize)

    sgr_randtest = sgr_testmap["frequency_within_block"].randtest
    sgr_p = sgr_randtest(bits, blocksize=blocksize)

    assert pclose(result.p, sgr_p)


@given(mixedbits())
def test_runs(bits):
    result = randtests.runs(bits)

    dj_randtest = dj_testmap["runs"].randtest
    dj_result = dj_randtest(bits)

    assert pclose(result.p, dj_result.p)

    sgr_randtest = sgr_testmap["runs"].randtest
    sgr_p = sgr_randtest(bits)

    assert pclose(result.p, sgr_p)


@given(mixedbits(min_size=128))
@settings(suppress_health_check=[HealthCheck.large_base_example])
def test_longest_runs(bits):
    result = randtests.longest_runs(pd.Series(bits))

    dj_randtest = dj_testmap["longest_runs"].randtest
    dj_result = dj_randtest(bits)

    assert pclose(result.p, dj_result.p)

    sgr_randtest = sgr_testmap["longest_runs"].randtest
    sgr_p = sgr_randtest(bits)

    assert pclose(result.p, sgr_p)


@given(matrix_strategy(min_blocks=38))
@settings(
    suppress_health_check=[
        HealthCheck.large_base_example,
        HealthCheck.data_too_large,
        HealthCheck.too_slow,
    ]
)
def test_dj_binary_matrix_rank(args):
    bits, matrix_dimen = args

    result = randtests.binary_matrix_rank(bits, matrix_dimen=matrix_dimen)

    dj_randtest = dj_testmap["binary_matrix_rank"].randtest

    try:
        dj_result = dj_randtest(bits, matrix_dimen=matrix_dimen)
        assert pclose(result.p, dj_result.p)
    except ImplementationError:
        pass


@given(matrix_strategy(min_blocks=38, square_matrix=True))
@settings(
    suppress_health_check=[
        HealthCheck.large_base_example,
        HealthCheck.data_too_large,
        HealthCheck.too_slow,
    ]
)
def test_sgr_binary_matrix_rank(args):
    bits, matrix_dimen = args

    result = randtests.binary_matrix_rank(bits, matrix_dimen=matrix_dimen)

    sgr_randtest = sgr_testmap["binary_matrix_rank"].randtest
    sgr_p = sgr_randtest(bits, matrix_dimen=matrix_dimen)

    assert pclose(result.p, sgr_p)


@given(mixedbits())
def test_discrete_fourier_transform(bits):
    if len(bits) % 2 != 0:
        truncated_bits = bits[:-1]
        assume(0 in truncated_bits and 1 in truncated_bits)

    result = randtests.discrete_fourier_transform(pd.Series(bits))

    dj_randtest = dj_testmap["discrete_fourier_transform"].randtest
    dj_result = dj_randtest(bits)

    assert pclose(result.p, dj_result.p)

    sgr_randtest = sgr_testmap["discrete_fourier_transform"].randtest
    sgr_p = sgr_randtest(bits)

    assert pclose(result.p, sgr_p)


dj_template_kwargs = dj_testmap["overlapping_template_matching"].fixedkwargs


# TODO figure out why test running incredibly slow, even with:
#      - maxexamples 1
#      - no shrinking phase
#      Maybe a problem with dj or our implementation?
# @given(template_strategy(**dj_template_kwargs))
# @settings(
#     suppress_health_check=[
#         HealthCheck.large_base_example,
#         HealthCheck.data_too_large,
#         HealthCheck.too_slow,
#     ]
# )
# def test_overlapping_template_matching(bits):
#     dj_implementation = dj_testmap["overlapping_template_matching"]
#     dj_randtest = dj_implementation.randtest
#     dj_fixedkwargs = dj_implementation.fixedkwargs

#     result = randtests.overlapping_template_matching(pd.Series(bits), **dj_fixedkwargs)

#     dj_result = dj_randtest(bits)

#     assert pclose(result.p, dj_result.p)


# TODO find out why dj differs p a fair bit
@given(universal_strategy())
@settings(suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow])
def test_maurers_universal(args):
    bits, blocksize, init_nblocks = args

    result = randtests.maurers_universal(
        pd.Series(bits), blocksize=blocksize, init_nblocks=init_nblocks
    )

    dj_randtest = dj_testmap["maurers_universal"].randtest
    dj_result = dj_randtest(bits, blocksize=blocksize, init_nblocks=init_nblocks)

    assert pclose(result.p, dj_result.p)
