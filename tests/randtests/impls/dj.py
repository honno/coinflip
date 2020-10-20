"""Adaptor of David Johnston's sts implementation

See David Johnston's `GitHub repository
<https://github.com/dj-on-github/sp800_22_tests>`_ for the original source code.
"""
# TODO configure single-line imports
# fmt: off
from functools import wraps
from typing import List
from typing import NamedTuple

from .core import Implementation
from .core import ImplementationError
from .sp800_22_tests.sp800_22_binary_matrix_rank_test import binary_matrix_rank_test as _binary_matrix_rank
from .sp800_22_tests.sp800_22_cumulative_sums_test import cumulative_sums_test as _cusum
from .sp800_22_tests.sp800_22_dft_test import dft_test as _spectral
from .sp800_22_tests.sp800_22_frequency_within_block_test import frequency_within_block_test as _frequency_within_block
from .sp800_22_tests.sp800_22_linear_complexity_test import linear_complexity_test as _linear_complexity
from .sp800_22_tests.sp800_22_longest_run_ones_in_a_block_test import longest_run_ones_in_a_block_test as _longest_runs
from .sp800_22_tests.sp800_22_maurers_universal_test import maurers_universal_test as _maurers_universal
from .sp800_22_tests.sp800_22_monobit_test import monobit_test as _monobit
from .sp800_22_tests.sp800_22_non_overlapping_template_matching_test import \
    non_overlapping_template_matching_test as _non_overlapping_template_matching
from .sp800_22_tests.sp800_22_overlapping_template_matching_test import \
    overlapping_template_matching_test as _overlapping_template_matching
from .sp800_22_tests.sp800_22_random_excursion_test import random_excursion_test as _random_excursions
from .sp800_22_tests.sp800_22_runs_test import runs_test as _runs
from .sp800_22_tests.sp800_22_serial_test import serial_test as _serial

# fmt: on

__all__ = ["testmap"]


class Result(NamedTuple):
    """Named tuple for test results in David Johnston's SP800-22 suite

    Notes
    -----
    ``p`` is assigned a ``float`` and ``pvalues`` is assigned ``None`` when only
    one p-value is returned. Otherwise ``p`` is assigned ``None`` and ``pvalues``
    is assigned a list of p-values.
    """

    success: bool
    p: float
    pvalues: List[float]


def return_p(randtest):
    @wraps(randtest)
    def wrapper(bits, *args, **kwargs):
        _result = randtest(bits, *args, **kwargs)
        result = Result(*_result)

        return result.p

    return wrapper


def return_pvalues(randtest):
    @wraps(randtest)
    def wrapper(bits, *args, **kwargs):
        _result = randtest(bits, *args, **kwargs)
        result = Result(*_result)

        return result.pvalues

    return wrapper


@return_p
def monobit(bits):
    return _monobit(bits)


@return_p
def frequency_within_block(bits):
    return _frequency_within_block(bits)


@return_p
def runs(bits):
    return _runs(bits)


@return_p
def longest_runs(bits):
    return _longest_runs(bits)


@return_p
def spectral(bits):
    return _spectral(bits)


@return_p
def binary_matrix_rank(bits, matrix_dimen):
    nrows, ncols = matrix_dimen
    nblocks = len(bits) // (nrows * ncols)
    if nblocks < 38:
        raise ImplementationError()

    try:
        return _binary_matrix_rank(bits, M=nrows, Q=ncols)
    except (ZeroDivisionError, IndexError, OverflowError) as e:
        raise ImplementationError(str(e)) from e


@return_p
def non_overlapping_template_matching(bits):
    return _non_overlapping_template_matching(bits)


@return_p
def overlapping_template_matching(bits):
    return _overlapping_template_matching(bits)


@return_p
def maurers_universal(bits, blocksize, init_nblocks):
    return _maurers_universal(bits, patternlen=blocksize, initblocks=init_nblocks)


@return_p
def linear_complexity(bits, blocksize):
    return _linear_complexity(bits, patternlen=blocksize)


def cusum(bits, reverse=False):
    _result = _cusum(bits)
    result = Result(*_result)

    if not reverse:
        return result.pvalues[0]
    else:
        return result.pvalues[1]


@return_pvalues
def serial(bits, blocksize):
    return _serial(bits, patternlen=blocksize)


@return_pvalues
def random_excursions(bits):
    return _random_excursions(bits)


testmap = {
    "monobit": Implementation(monobit),
    "frequency_within_block": Implementation(
        frequency_within_block, fixedkwargs={"blocksize": 20}
    ),
    "runs": Implementation(runs),
    "longest_runs": Implementation(longest_runs),
    "binary_matrix_rank": Implementation(binary_matrix_rank),
    "spectral": Implementation(spectral),
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
    "linear_complexity": Implementation(linear_complexity),
    "cusum": Implementation(cusum),
    "serial": Implementation(serial),
    "random_excursions": Implementation(random_excursions),
}
