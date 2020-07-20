"""Adaptor of David Johnston's sts implementation

See David Johnston's `GitHub repository
<https://github.com/dj-on-github/sp800_22_tests>`_ for the original source code.
"""
from functools import wraps
from typing import NamedTuple

# fmt: off
from ._implementation import Implementation
from ._implementation import ImplementationError
from .sp800_22_tests.sp800_22_binary_matrix_rank_test import binary_matrix_rank_test as _binary_matrix_rank
from .sp800_22_tests.sp800_22_dft_test import dft_test as _discrete_fourier_transform
from .sp800_22_tests.sp800_22_frequency_within_block_test import frequency_within_block_test as _frequency_within_block
from .sp800_22_tests.sp800_22_longest_run_ones_in_a_block_test import longest_run_ones_in_a_block_test as _longest_runs
from .sp800_22_tests.sp800_22_maurers_universal_test import maurers_universal_test as _maurers_universal
from .sp800_22_tests.sp800_22_monobit_test import monobit_test as _monobits
from .sp800_22_tests.sp800_22_non_overlapping_template_matching_test import \
    non_overlapping_template_matching_test as _non_overlapping_template_matching
from .sp800_22_tests.sp800_22_overlapping_template_matching_test import \
    overlapping_template_matching_test as _overlapping_template_matching
from .sp800_22_tests.sp800_22_runs_test import runs_test as _runs

# fmt: on

__all__ = ["testmap"]


class DJResult(NamedTuple):
    success: bool
    p: float
    unknown: None


def named(randtest):
    @wraps(randtest)
    def wrapper(bits, *args, **kwargs):
        result = randtest(bits, *args, **kwargs)

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
def longest_runs(bits):
    return _longest_runs(bits)


@named
def discrete_fourier_transform(bits):
    return _discrete_fourier_transform(bits)


@named
def binary_matrix_rank(bits, matrix_dimen):
    nrows, ncols = matrix_dimen
    nblocks = len(bits) // (nrows * ncols)
    if nblocks < 38:
        raise ImplementationError()

    try:
        return _binary_matrix_rank(bits, M=nrows, Q=ncols)
    except (ZeroDivisionError, IndexError) as e:
        raise ImplementationError() from e


@named
def non_overlapping_template_matching(bits):
    return _non_overlapping_template_matching(bits)


@named
def overlapping_template_matching(bits):
    return _overlapping_template_matching(bits)


@named
def maurers_universal(bits, blocksize, init_nblocks):
    return _maurers_universal(bits, patternlen=blocksize, initblocks=init_nblocks)


testmap = {
    "monobits": Implementation(monobits),
    "frequency_within_block": Implementation(
        frequency_within_block, fixedkwargs={"blocksize": 20}
    ),
    "runs": Implementation(runs),
    "longest_runs": Implementation(longest_runs),
    "binary_matrix_rank": Implementation(binary_matrix_rank),
    "discrete_fourier_transform": Implementation(discrete_fourier_transform),
    "non_overlapping_template_matching": Implementation(
        non_overlapping_template_matching,
        missingkwargs=["template"],
        fixedkwargs={"nblocks": 8},
    ),
    "overlapping_template_matching": Implementation(
        overlapping_template_matching,
        fixedkwargs={"template": [1 for x in range(10)], "nblocks": 968},
    ),
    "maurers_universal": Implementation(maurers_universal),
}
