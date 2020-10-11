"""Utility methods for randomness tests."""
from dataclasses import dataclass
from functools import lru_cache
from functools import wraps
from math import ceil
from typing import Any
from typing import Dict
from typing import Iterator
from typing import Tuple
from warnings import warn

import pandas as pd

from coinflip._randtests.common.exceptions import NonBinarySequenceError
from coinflip._randtests.common.exceptions import TestInputError
from coinflip._randtests.common.result import BaseTestResult

__all__ = [
    "randtest",
    "infer_faces",
    "check_recommendations",
    "blocks",
    "rawblocks",
    "slider",
]


@dataclass
class MinimumInputError(TestInputError):
    n: int
    min_n: int

    def __str__(self):
        return f"Sequence length {self.n} is below required minimum of {self.min_n}"


def randtest(min_n=2):
    """Decorator factory for parsing sequences in randomness tests

    Returns a decorator (a method which returns a wrapper method). The wrapper
    checks if passed ``sequence`` is a pandas ``Series``, attempting to convert
    it if not.

    The length of the ``sequence`` is then checked to see if it meets the
    passed minimum input requirement, raising an error if not.

    The `heads` and `tails` of the ``sequence`` is inferred from its unique
    values.

    Parameters
    ----------
    min_n : ``int``, default ``2``
        Minimum length of sequence the test can handle

    Returns
    -------
    decorator : ``Callable[[Callable], Callable]``
        Decorator method for parsing sequences in randomness tests

    Raises
    ------
    MinimumInputError
        If ``sequence`` length exceeds ``min_n``

    See Also
    --------
    pandas.Series: Initialises with ``sequence`` if not already a ``Series``

    Notes
    -----
    `heads` and `tails` corresponds to the ``1`` and ``0`` values of a binary
    input sequence. SP800-22 only specifies randomness tests for these binary
    sequences, but in actuality all of its tests can be generalised for any
    sequence of a GF(2) field (i.e. contains two distinct values), so the
    `heads` and `tails` abstraction allows for mapping these GF(2) sequences to
    their binary counterparts.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(sequence, *args, **kwargs) -> BaseTestResult:
            if isinstance(sequence, pd.Series):
                series = sequence
            else:
                series = pd.Series(sequence)

            if series.nunique() != 2:
                raise NonBinarySequenceError()

            n = len(series)
            if n < min_n:
                raise MinimumInputError(n, min_n)

            values = series.unique()
            heads, tails = infer_faces(tuple(values))

            result = func(series, heads, tails, *args, **kwargs)

            return result

        return wrapper

    return decorator


@lru_cache()
def infer_faces(unique_values: Tuple[Any, Any]):
    """Infers the `heads` and `tails` faces from a list of unique values

    An equality check between the values is attempted where the "largest"
    value is chosen as the `heads`, and subsequently the other value is
    chosen as the `tails`.

    Parameters
    ----------
    unique_values : ``Tuple[Any, Any]``
        Tuple of two unique values

    Returns
    -------
    heads
        Inferred heads face of ``unique_values``
    tails
        Inferred tails face of ``unique_values``
    """
    heads = max(unique_values)
    tails = next(value for value in unique_values if value != heads)

    return heads, tails


def check_recommendations(recommendations: Dict[str, bool]):
    """Warns on recommendation failures

    Parameters
    ----------
    recommendations : ``Dict[str, bool]``
        Map of recommendation string representations to the actual
        recommendation outcomes

    Warns
    -----
    UserWarning
        When one or more recommendations fail
    """
    failures = [expr for expr, success in recommendations.items() if not success]

    nfail = len(failures)
    if nfail == 1:
        expr = failures[0]
        warn(f"NIST recommendation not met: {expr}", UserWarning)

    elif nfail > 1:
        msg = "Multiple NIST recommendations not met:\n"
        msg += "\n".join([f"\t• {expr}" for expr in failures])
        warn(msg, UserWarning)


def blocks(series, blocksize=None, nblocks=None, truncate=True) -> Iterator[pd.Series]:
    """Chunking method for ``Series`` objects

    Parameters
    ----------
    series : ``Series``
        The pandas ``Series`` to chunk
    blocksize : ``int``, required if no ``nblocks`` passed
        Size of the chunks
    nblocks : ``int``, required if no ``blocksize`` passed
        Number of chunks
    truncate : ``bool``, default ``True``
        Whether to discard remaning series

    Yields
    ------
    block : ``Series``
        Chunk of the passed ``series``

    Raises
    ------
    ValueError
        When neither ``blocksize`` or ``nblocks`` is passed
    """
    n = len(series)

    if not blocksize and not nblocks:
        raise ValueError("Either blocksize or nblocks must be specified")
    elif nblocks is None:
        nblocks = n // blocksize
    elif blocksize is None:
        blocksize = ceil(n / nblocks)

    boundary = blocksize * nblocks

    for i in range(0, boundary, blocksize):
        yield series[i : i + blocksize]

    if not truncate and boundary < n:
        yield series[boundary:]


def rawblocks(*args, **kwargs) -> Iterator[Tuple[Any]]:
    """Tuple chunking method for ``Series`` objects

    Parameters
    ----------
    *args
        Positional arguments to pass to ``blocks``
    **kwargs
        Keyword arguments to pass to ``blocks``

    Yields
    ------
    block_tup : ``Tuple``
        Tuple representation of the block

    Raises
    ------
    ValueError
        When neither ``blocksize`` or ``nblocks`` is passed

    See Also
    --------
    blocks: The method ``rawblocks`` adapts
    """

    for block in blocks(*args, **kwargs):
        block_tup = tuple(block)

        yield block_tup


# TODO desc
def slider(series, window_size, overlap=False) -> Iterator[Tuple[Any]]:
    boundary = len(series) - window_size + 1
    step = 1 if overlap else window_size
    for pointer in range(0, boundary, step):
        window = series[pointer : pointer + window_size]
        window_tup = tuple(window)

        yield window_tup
