from dataclasses import dataclass
from functools import wraps
from math import ceil

import pandas as pd

__all__ = ["TestResult", "stattest", "binary_stattest", "chunks"]


@dataclass
class TestResult:
    p: float

    def p2f(self):
        return round(self.p, 2)

    def __str__(self):
        raise NotImplementedError()

    def report(self):
        raise NotImplementedError()


def stattest(func):
    @wraps(func)
    def wrapper(series: pd.Series, *args, **kwargs):
        if series.nunique() == 1:
            raise ValueError()

        result = func(series, *args, **kwargs)

        return result

    return wrapper


def binary_stattest(func):
    @wraps(func)
    def wrapper(series: pd.Series, *args, **kwargs):
        if series.nunique() != 2:
            raise ValueError()

        result = func(series, *args, **kwargs)

        return result

    return wrapper


def chunks(series: pd.Series, block_size=None, nblocks=None):
    if block_size and nblocks:
        raise ValueError()
    elif not block_size and not nblocks:
        raise ValueError()

    if block_size is None:
        block_size = ceil(len(series) / nblocks)

    for i in range(0, len(series), block_size):
        yield series[i : i + block_size]
