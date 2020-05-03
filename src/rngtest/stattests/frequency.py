from dataclasses import dataclass
from math import ceil
from math import erfc
from math import sqrt
from typing import Any
from typing import NamedTuple

import pandas as pd

from rngtest.stattests.summary import Result


class ValueCount(NamedTuple):
    value: Any
    count: int


@dataclass
class FreqResult(Result):
    counts: pd.Series

    def __post_init__(self):
        self.maxcount = ValueCount(
            value=self.counts.index.values[0], count=self.counts.values[0]
        )
        self.mincount = ValueCount(
            value=self.counts.index.values[-1], count=self.counts.values[-1]
        )

    def summary(self):
        return (
            f"p={self.p}\n"
            f"{self.maxcount.value} had the highest frequency of {self.maxcount.count}"
        )


def frequency(series):
    counts = series.value_counts()

    if series.nunique() != 2:
        raise NotImplementedError()
    else:
        n = len(series)
        Sn = counts.iloc[0] - counts.iloc[1]
        statistic = abs(Sn) / sqrt(n)
        p = erfc(statistic / sqrt(2))

        return FreqResult(p=p, counts=counts)


def frequency_in_block(series, block_size=None, nblocks=10):
    if block_size is None:
        block_size = ceil(len(series) / nblocks)

    while len(series) != 0:
        series_block, series = series[:block_size], series[block_size:]

        frequency(series_block)

    # TODO summary statistics
