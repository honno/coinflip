from math import ceil

import pandas as pd

__all__ = ["chunks"]


def chunks(series: pd.Series, blocksize=None, nblocks=None):
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
