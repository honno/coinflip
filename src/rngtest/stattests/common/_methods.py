from math import ceil

import pandas as pd

__all__ = ["chunks"]


def chunks(series: pd.Series, block_size=None, nblocks=None):
    if block_size and nblocks:
        raise ValueError()
    elif not block_size and not nblocks:
        raise ValueError()

    if block_size is None:
        block_size = ceil(len(series) / nblocks)

    elements_remaining = len(series) % block_size
    boundary = len(series) - elements_remaining

    for i in range(0, boundary, block_size):
        yield series[i : i + block_size]
