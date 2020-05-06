from dataclasses import dataclass
from math import ceil
from math import erfc
from math import sqrt
from typing import Any
from typing import NamedTuple

import pandas as pd

from rngtest.stattests.summary import TestResult


def frequency(series):
    counts = series.value_counts()

    if series.nunique() != 2:
        return FrequencyTestResult(p=None, counts=counts)
    else:
        n = len(series)
        difference = counts.iloc[0] - counts.iloc[1]
        statistic = abs(difference) / sqrt(n)
        p = erfc(statistic / sqrt(2))

        return MonobitTestResult(p=p, counts=counts)


class ValueCount(NamedTuple):
    value: Any
    count: int


@dataclass
class BaseFrequencyTestResult(TestResult):
    counts: pd.Series

    def __post_init__(self):
        self.maxcount = ValueCount(
            value=self.counts.index.values[0], count=self.counts.values[0]
        )
        self.mincount = ValueCount(
            value=self.counts.index.values[-1], count=self.counts.values[-1]
        )


class MonobitTestResult(BaseFrequencyTestResult):
    def __str__(self):
        return (
            f"p={self.p2f()}\n"
            f"{self.maxcount.value} occurred {self.maxcount.count} times\n"
            f"{self.mincount.value} occurred {self.mincount.count} times"
        )


class FrequencyTestResult(BaseFrequencyTestResult):
    def __str__(self):
        return (
            f"{self.maxcount.value} occurred the most ({self.maxcount.count} times)\n"
            f"{self.mincount.value} occurred the least ({self.mincount.count} times)"
        )


def frequency_in_block(series, block_size=None, nblocks=10):
    if block_size is None:
        block_size = ceil(len(series) / nblocks)

    while len(series) != 0:
        series_block, series = series[:block_size], series[block_size:]

        frequency(series_block)

    # TODO summary statistics
