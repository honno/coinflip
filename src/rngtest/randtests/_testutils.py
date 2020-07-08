"""Utility methods for randomness tests."""
from math import ceil
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Tuple
from warnings import warn

import pandas as pd

__all__ = ["blocks", "rawblocks", "check_recommendations"]


def blocks(series, blocksize=None, nblocks=None, truncate=True) -> Iterable[pd.Series]:
    """Chunking method for `Series` objects

    Parameters
    ----------
    series : `Series`
        The pandas `Series` to chunk
    blocksize : `int`, required if no `nblocks` passed
        Size of the chunks
    nblocks : `int`, required if no `blocksize` passed
        Number of chunks
    truncate : `bool`, default `True`
        Whether to discard remaning series

    Yields
    ------
    block : `Series`
        Chunk of the passed `series`

    Raises
    ------
    ValueError
        When neither `blocksize` or `nblocks` is passed
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


def rawblocks(*args, **kwargs) -> Iterable[Tuple[Any]]:
    """Tuple chunking method for `Series` objects

    Parameters
    ----------
    *args
        Positional arguments to pass to `blocks`
    **kwargs
        Keyword arguments to pass to `blocks`

    Yields
    ------
    block_tup : `Tuple`
        Tuple representation of the block

    Raises
    ------
    ValueError
        When neither `blocksize` or `nblocks` is passed

    See Also
    --------
    blocks: The method `rawblocks` adapts
    """

    for block in blocks(*args, **kwargs):
        block_list = block.tolist()
        block_tup = tuple(block_list)

        yield block_tup


def check_recommendations(recommendation: Dict[str, bool]):
    """Warns on recommendation failures

    Parameters
    ----------
    recommendations : `Dict[str, bool]`
        Map of recommendation string representations to the actual
        recommendation outcomes

    Warns
    -----
    UserWarning
        When one or more recommendations fail
    """
    failures = [expr for expr, success in recommendation.items() if not success]

    nfail = len(failures)
    if nfail == 1:
        expr = failures[0]
        warn(f"NIST recommendation not met: {expr}", UserWarning)

    elif nfail > 1:
        msg = "Multiple NIST recommendations not met:\n"
        msg += "\n".join([f"\t• {expr}" for expr in failures])
        warn(msg, UserWarning)
