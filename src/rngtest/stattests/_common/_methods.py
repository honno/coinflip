from math import ceil
from typing import Any
from typing import Iterable
from typing import Tuple

import pandas as pd

__all__ = ["blocks", "rawblocks"]


def blocks(series: pd.Series, blocksize=None, nblocks=None) -> Iterable[pd.Series]:
    if not blocksize and not nblocks:
        raise ValueError()
    elif nblocks is None:
        nblocks = len(series) // blocksize
    elif blocksize is None:
        blocksize = ceil(len(series) / nblocks)

    boundary = blocksize * nblocks

    for i in range(0, boundary, blocksize):
        yield series[i : i + blocksize]


def rawblocks(*args, **kwargs) -> Iterable[Tuple[Any]]:
    for block in blocks(*args, **kwargs):
        block_list = block.tolist()
        block_tup = tuple(block_list)

        yield block_tup
