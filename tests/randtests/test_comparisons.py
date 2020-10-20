"""Compares results of our tests to those of other implementations"""
from dataclasses import dataclass
from math import log
from typing import Dict
from typing import List
from typing import Tuple

from hypothesis import HealthCheck
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from pytest import mark
from pytest import skip

from coinflip import randtests

from .impls import testmaps
from .impls.core import ImplementationError
from .strategies import mixedbits

ArgsStrategy = SearchStrategy[Tuple[List, Dict]]


@st.composite
def bits_strategy(draw, min_n=2) -> ArgsStrategy:
    bits = draw(mixedbits(min_size=min_n))

    return bits, {}


@st.composite
def blocksize_strategy(draw, min_n=2) -> ArgsStrategy:
    bits = draw(mixedbits(min_size=min_n))

    n = len(bits)

    blocksize = draw(st.integers(min_value=1, max_value=n))

    return bits, {"blocksize": blocksize}


@st.composite
def matrix_strategy(draw) -> ArgsStrategy:
    max_blocksize = draw(st.integers(min_value=4, max_value=1000000))

    naxis1 = draw(st.integers(min_value=2, max_value=max_blocksize // 2))
    naxis2 = max_blocksize // naxis1

    if draw(st.booleans()):
        nrows = naxis1
        ncols = naxis2
    else:
        ncols = naxis1
        nrows = naxis2

    blocksize = nrows * ncols
    bits = draw(mixedbits(min_size=blocksize))

    matrix_dimen = (nrows, ncols)

    return bits, {"matrix_dimen": matrix_dimen}


stratmap = {
    "monobit": bits_strategy(),
    "frequency_within_block": blocksize_strategy(min_n=8),
    "runs": bits_strategy(),
    "longest_runs": bits_strategy(min_n=128),
    "binary_matrix_rank": matrix_strategy(),
}


@dataclass
class AdaptorError(TypeError):
    author: str
    _e: TypeError

    def __str__(self):
        message = str(self._e)
        return f"{self.author}'s {message}"


@mark.parametrize(["randtest", "strategy"], stratmap.items())
@given(data=st.data())
@settings(
    deadline=None,
    suppress_health_check=[HealthCheck.data_too_large, HealthCheck.too_slow],
)
def test_comparisons(randtest, strategy, data):
    implementations = {}
    for author, testmap in testmaps.items():
        try:
            implementation = testmap[randtest]
            implementations[author] = implementation
        except KeyError:
            pass

    if not implementations:
        skip()

    bits, kwargs = data.draw(strategy)

    coinflip_randtest = getattr(randtests, randtest)
    coinflip_result = coinflip_randtest(bits, **kwargs)

    implementation_results = {}
    for author, implementation in implementations.items():
        if implementation.missingkwargs or implementation.fixedkwargs:
            continue

        try:
            p = implementation.randtest(bits, **kwargs)
            implementation_results[author] = p
        except ImplementationError:
            pass
        except TypeError as e:
            raise AdaptorError(author, e) from e

    for author, p in implementation_results.items():
        assert pclose(coinflip_result.p, p)


def pclose(p1: float, p2: float) -> bool:
    """Finds if two p-values are reasonably close to each other

    Small p-values tend to vary widely accross implementations, and so the
    closeness margin is more lenient the closer the p-values are to 0."""
    p_avg = (p1 + p2) / 2
    margin = max(-log(p_avg), 0.05)
    diff = abs(p1 - p2)

    return diff < margin
