from math import isclose
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import NamedTuple

import pandas as pd
from hypothesis import assume
from hypothesis import given

from rngtest.stattests import fourier
from rngtest.stattests import frequency
from rngtest.stattests import runs

from .implementations import dj
from .strategies import random_bits_strategy

__all__ = ["Implementation"]


class Implementation(NamedTuple):
    stattest: Callable
    missingkwargs: List[str] = []
    fixedkwargs: Dict[str, Any] = {}


@given(random_bits_strategy)
def test_monobits(bits):
    our_result = frequency.monobits(pd.Series(bits))
    dj_result = dj.monobit_test(bits)

    assert isclose(our_result.p, dj_result.p)


# TODO figure out sensible isclose margins for extreme sequence inputs
# @given(large_random_bits_strategy)
# def test_frequency_within_block(bits):
#     our_result = frequency.frequency_within_block(pd.Series(bits), blocksize=dj.blocksize)
#     dj_result = dj.frequency_within_block_test(bits)

#     assert isclose(our_result.p, dj_result.p, abs_tol=0.005)


@given(random_bits_strategy)
def test_runs(bits):
    our_result = runs.runs(pd.Series(bits))
    dj_result = dj.runs_test(bits)

    assert isclose(our_result.p, dj_result.p)


@given(random_bits_strategy)
def test_discrete_fourier_transform(bits):
    if len(bits) % 2 != 0:
        truncated_bits = bits[:-1]
        assume(0 in truncated_bits and 1 in truncated_bits)

    our_result = fourier.discrete_fourier_transform(pd.Series(bits))
    dj_result = dj.fourier_test(bits)

    assert isclose(our_result.p, dj_result.p)
