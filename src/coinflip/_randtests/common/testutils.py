"""Utility methods for randomness tests."""
from typing import Any
from typing import Iterator
from typing import Tuple

import pandas as pd

__all__ = [
    "blocks",
    "rawblocks",
    "slider",
]


def blocks(series, blocksize, truncate=True) -> Iterator[pd.Series]:
    """Chunking method for ``Series`` objects

    Parameters
    ----------
    series : ``Series``
        The pandas ``Series`` to chunk
    blocksize : ``Integer``
        Size of the chunks
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
    nblocks = n // blocksize
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


def slider(series, window_size) -> Iterator[Tuple[Any]]:
    if window_size != 0:
        boundary = len(series) - window_size + 1
        for pointer in range(0, boundary, 1):
            window = series[pointer : pointer + window_size]
            window_tup = tuple(window)

            yield window_tup
