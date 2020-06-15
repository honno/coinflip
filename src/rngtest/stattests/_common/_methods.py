from math import ceil
from typing import Any
from typing import Iterable
from typing import Tuple

import pandas as pd

__all__ = ["chunks", "rawchunks"]


def chunks(series: pd.Series, blocksize=None, nblocks=None) -> Iterable[pd.Series]:
    if blocksize and nblocks:
        raise ValueError()
    elif not blocksize and not nblocks:
        raise ValueError()

    if blocksize is None:
        blocksize = ceil(len(series) / nblocks)

    elements_remaining = len(series) % blocksize
    boundary = len(series) - elements_remaining

    for i in range(0, boundary, blocksize):

        yield series[i : i + blocksize]


def rawchunks(*args, **kwargs) -> Iterable[Tuple[Any]]:
    for chunk in chunks(*args, **kwargs):
        chunk_list = chunk.tolist()
        chunk_tuple = tuple(chunk_list)

        yield chunk_tuple
