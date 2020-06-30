from math import ceil
from typing import Any
from typing import Dict
from typing import Iterable
from typing import Tuple
from warnings import warn

import pandas as pd

__all__ = ["blocks", "rawblocks", "check_recommendation"]


def blocks(series, blocksize=None, nblocks=None, cutoff=True) -> Iterable[pd.Series]:
    n = len(series)

    if not blocksize and not nblocks:
        raise ValueError()
    elif nblocks is None:
        nblocks = n // blocksize
    elif blocksize is None:
        blocksize = ceil(n / nblocks)

    boundary = blocksize * nblocks

    for i in range(0, boundary, blocksize):
        yield series[i : i + blocksize]

    if not cutoff and boundary < n:
        yield series[boundary:]


def rawblocks(*args, **kwargs) -> Iterable[Tuple[Any]]:
    for block in blocks(*args, **kwargs):
        block_list = block.tolist()
        block_tup = tuple(block_list)

        yield block_tup


def check_recommendation(recommendation: Dict[str, bool]):
    for expr, success in recommendation.items():
        if not success:
            warn(f"Failed NIST recommendation {expr}", UserWarning)
