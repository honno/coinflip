from functools import wraps
from typing import NamedTuple

import rngtest.stattests as stattests

# fmt: off
from ..test_compare_implementations import Implementation
from .sp800_22_tests.sp800_22_dft_test import dft_test as _discrete_fourier_transform
from .sp800_22_tests.sp800_22_frequency_within_block_test import frequency_within_block_test as _frequency_within_block
from .sp800_22_tests.sp800_22_monobit_test import monobit_test as _monobits
from .sp800_22_tests.sp800_22_runs_test import runs_test as _runs

# fmt: on

__all__ = ["testmap"]


class DJResult(NamedTuple):
    success: bool
    p: float
    unknown: None


def named(stattest):
    @wraps(stattest)
    def wrapper(bits):
        result = stattest(bits)

        return DJResult(*result)

    return wrapper


@named
def monobits(bits):
    return _monobits(bits)


@named
def frequency_within_block(bits):
    return _frequency_within_block(bits)


@named
def runs(bits):
    return _runs(bits)


@named
def discrete_fourier_transform(bits):
    return _discrete_fourier_transform(bits)


testmap = {
    stattests.frequency.monobits: Implementation(monobits),
    stattests.frequency.frequency_within_block: Implementation(
        frequency_within_block, fixedkwargs=dict(blocksize=20)
    ),
    stattests.runs.runs: Implementation(runs),
    stattests.fourier.discrete_fourier_transform: Implementation(
        discrete_fourier_transform
    ),
}
