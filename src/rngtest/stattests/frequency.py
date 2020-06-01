from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any
from typing import NamedTuple

import pandas as pd
from scipy.special import gammaincc

from rngtest.stattests.common.decorators import binary_stattest
from rngtest.stattests.common.decorators import elected
from rngtest.stattests.common.methods import chunks
from rngtest.stattests.common.result import TestResult
from rngtest.stattests.common.result import erfc_plot
from rngtest.stattests.common.result import half_norm_plot

__all__ = ["monobits", "frequency_within_block"]


@binary_stattest
def monobits(series):
    counts = series.value_counts()

    n = len(series)
    difference = abs(counts.iloc[0] - counts.iloc[1])
    statistic = difference / sqrt(n)
    p = erfc(statistic / sqrt(2))

    return MonobitsTestResult(statistic=statistic, p=p, counts=counts)


@elected
@binary_stattest
def frequency_within_block(series, candidate, block_size=8):
    if len(series) < 100:
        raise ValueError()

    nblocks = len(series) // block_size

    proportions = []
    for chunk in chunks(series, block_size=block_size):
        count = (chunk == candidate).sum()
        prop = count / block_size
        proportions.append(prop)

    deviations = (prop - 1 / 2 for prop in proportions)

    statistic = 4 * block_size * sum(x ** 2 for x in deviations)
    p = gammaincc(nblocks / 2, statistic / 2)

    return TestResult(statistic=statistic, p=p)


class ValueCount(NamedTuple):
    value: Any
    count: int


@dataclass
class MonobitsTestResult(TestResult):
    counts: pd.Series

    def __post_init__(self):
        self.maxcount = ValueCount(
            value=self.counts.index.values[0], count=self.counts.values[0]
        )
        self.mincount = ValueCount(
            value=self.counts.index.values[-1], count=self.counts.values[-1]
        )

    def __str__(self):
        return (
            f"p={self.p3f()}\n"
            f"{self.maxcount.value} occurred {self.maxcount.count} times\n"
            f"{self.mincount.value} occurred {self.mincount.count} times"
        )

    def _report(self):
        return [
            f"p={self.p3f()}",
            self.counts.plot(kind="bar"),
            half_norm_plot(self.statistic),
            erfc_plot(self.statistic / sqrt(2)),
        ]
