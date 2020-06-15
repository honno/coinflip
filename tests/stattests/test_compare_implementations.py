from math import ceil
from math import floor
from math import log
from math import log2

import pandas as pd
from hypothesis import HealthCheck
from hypothesis import assume
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

import rngtest.stattests as stattests

from .implementations import ImplementationError
from .implementations import dj_testmap
from .implementations import sgr_testmap


def pclose(left, right) -> bool:
    p_avg = (left + right) / 2
    margin = max(-log(p_avg), 0.05)
    diff = abs(left - right)

    return diff < margin


# -------------------
# Strategy definition
# -------------------


def contains_multiple_values(array):
    firstval = array[0]
    for val in array[1:]:
        if val != firstval:
            return True
    else:
        return False


def mixedbits(min_size=2):
    binary = st.integers(min_value=0, max_value=1)
    bits = st.lists(binary, min_size=min_size)
    mixedbits = bits.filter(contains_multiple_values)

    return mixedbits


@st.composite
def blocks_strategy(draw, min_size=2):
    bits = draw(mixedbits(min_size=min_size))

    n = len(bits)

    blocksize = draw(st.integers(min_value=1, max_value=n))

    return bits, blocksize


@st.composite
def matrix_strategy(draw, min_blocks=1, square_matrix=False):
    nblocks = draw(st.integers(min_value=min_blocks))

    if square_matrix:
        nrows = floor(log2(nblocks))
        ncols = nrows
    else:
        nrows = draw(st.integers(min_value=1, max_value=nblocks))
        ncols = max(ceil(nblocks / nrows), 2)

    blocksize = nrows * ncols
    n = nblocks * blocksize
    bits = draw(mixedbits(min_size=n))

    return bits, nrows, ncols


@st.composite
def template_strategy(draw, template, nblocks):
    templatesize = len(template)
    n = nblocks * templatesize

    bits = draw(mixedbits(min_size=n))

    return bits


@st.composite
def universal_strategy(draw, min_blocks=2):
    nblocks = draw(st.integers(min_value=min_blocks))

    blocksize = draw(st.integers(min_value=2))

    init_nblocks = draw(st.integers(min_value=1, max_value=nblocks - 1))

    n = nblocks * blocksize
    bits = draw(mixedbits(min_size=n))

    return bits, blocksize, init_nblocks


# ----------------
# Property testing
# ----------------


@given(mixedbits())
def test_monobits(bits):
    result = stattests.monobits(pd.Series(bits))

    dj_stattest = dj_testmap["monobits"].stattest
    dj_result = dj_stattest(bits)

    assert pclose(result.p, dj_result.p)

    sgr_stattest = sgr_testmap["monobits"].stattest
    sgr_p = sgr_stattest(bits)

    assert pclose(result.p, sgr_p)


@given(mixedbits(min_size=100))
def test_dj_frequency_within_block(bits):
    _implementation = dj_testmap["frequency_within_block"]
    dj_stattest = _implementation.stattest
    dj_fixedkwargs = _implementation.fixedkwargs

    result = stattests.frequency_within_block(pd.Series(bits), **dj_fixedkwargs)
    dj_result = dj_stattest(bits)

    assert pclose(result.p, dj_result.p)


@given(blocks_strategy(min_size=100))
def test_sgr_frequency_within_block(args):
    bits, blocksize = args

    result = stattests.frequency_within_block(bits, blocksize=blocksize)

    sgr_stattest = sgr_testmap["frequency_within_block"].stattest
    sgr_p = sgr_stattest(bits, blocksize=blocksize)

    assert pclose(result.p, sgr_p)


@given(mixedbits())
def test_runs(bits):
    result = stattests.runs(bits)

    dj_stattest = dj_testmap["runs"].stattest
    dj_result = dj_stattest(bits)

    assert pclose(result.p, dj_result.p)

    sgr_stattest = sgr_testmap["runs"].stattest
    sgr_p = sgr_stattest(bits)

    assert pclose(result.p, sgr_p)


@given(mixedbits(min_size=128))
@settings(suppress_health_check=[HealthCheck.large_base_example])
def test_longest_runs(bits):
    result = stattests.longest_runs(pd.Series(bits))

    dj_stattest = dj_testmap["longest_runs"].stattest
    dj_result = dj_stattest(bits)

    assert pclose(result.p, dj_result.p)

    sgr_stattest = sgr_testmap["longest_runs"].stattest
    sgr_p = sgr_stattest(bits)

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
    bits, nrows, ncols = args

    result = stattests.binary_matrix_rank(pd.Series(bits), nrows=nrows, ncols=ncols)

    dj_stattest = dj_testmap["binary_matrix_rank"].stattest

    try:
        dj_result = dj_stattest(bits, nrows=nrows, ncols=ncols)
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
    bits, nrows, ncols = args

    result = stattests.binary_matrix_rank(bits, nrows=nrows, ncols=ncols)

    sgr_stattest = sgr_testmap["binary_matrix_rank"].stattest
    sgr_p = sgr_stattest(bits, nrows=nrows, ncols=ncols)

    assert pclose(result.p, sgr_p)


@given(mixedbits())
def test_discrete_fourier_transform(bits):
    if len(bits) % 2 != 0:
        truncated_bits = bits[:-1]
        assume(0 in truncated_bits and 1 in truncated_bits)

    result = stattests.discrete_fourier_transform(pd.Series(bits))

    dj_stattest = dj_testmap["discrete_fourier_transform"].stattest
    dj_result = dj_stattest(bits)

    assert pclose(result.p, dj_result.p)

    sgr_stattest = sgr_testmap["discrete_fourier_transform"].stattest
    sgr_p = sgr_stattest(bits)

    assert pclose(result.p, sgr_p)


dj_template_kwargs = dj_testmap["overlapping_template_matching"].fixedkwargs


@given(template_strategy(**dj_template_kwargs))
@settings(
    suppress_health_check=[
        HealthCheck.large_base_example,
        HealthCheck.data_too_large,
        HealthCheck.too_slow,
    ]
)
def test_overlapping_template_matching(bits):
    dj_implementation = dj_testmap["overlapping_template_matching"]
    dj_stattest = dj_implementation.stattest
    dj_fixedkwargs = dj_implementation.fixedkwargs

    result = stattests.overlapping_template_matching(pd.Series(bits), **dj_fixedkwargs)

    dj_result = dj_stattest(bits)

    assert pclose(result.p, dj_result.p)


@given(universal_strategy())
@settings(suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow])
def test_maurers_universal(args):
    bits, blocksize, init_nblocks = args

    result = stattests.maurers_universal(
        pd.Series(bits), blocksize=blocksize, init_nblocks=init_nblocks
    )

    dj_stattest = dj_testmap["maurers_universal"].stattest
    dj_result = dj_stattest(bits, blocksize=blocksize, init_nblocks=init_nblocks)

    assert pclose(result.p, dj_result.p)
