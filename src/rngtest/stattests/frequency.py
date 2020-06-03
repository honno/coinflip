from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any
from typing import List
from typing import NamedTuple

import matplotlib.pyplot as plt
import pandas as pd
from scipy.special import gammaincc

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks
from rngtest.stattests.common import elected
from rngtest.stattests.common import plot_chi2
from rngtest.stattests.common import plot_erfc
from rngtest.stattests.common import plot_gammaincc
from rngtest.stattests.common import plot_halfnorm

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

    occurences = []
    for chunk in chunks(series, block_size=block_size):
        count = (chunk == candidate).sum()
        occurences.append(count)

    proportions = (count / block_size for count in occurences)

    deviations = (prop - 1 / 2 for prop in proportions)

    statistic = 4 * block_size * sum(x ** 2 for x in deviations)
    p = gammaincc(nblocks / 2, statistic / 2)

    return FrequencyWithinBlockTestResult(
        statistic=statistic,
        p=p,
        candidate=candidate,
        block_size=block_size,
        nblocks=nblocks,
        occurences=occurences,
    )


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
            plot_halfnorm(self.statistic),
            plot_erfc(self.statistic / sqrt(2)),
        ]


@dataclass
class FrequencyWithinBlockTestResult(TestResult):
    candidate: Any
    block_size: int
    nblocks: int
    occurences: List[int]

    def __str__(self):
        return f"p={self.p3f()}"

    def _report(self):
        occurfig, occurax = plt.subplots()

        x_axis = [i * self.block_size for i in range(len(self.occurences))]

        occurax.set_ylim([0, self.block_size])
        occurax.bar(x_axis, self.occurences, width=self.block_size * 0.9, align="edge")
        occurax.axhline(self.block_size / 2, color="black")

        return [
            f"p={self.p3f()}",
            occurfig,
            plot_chi2(self.statistic, df=self.nblocks),
            plot_gammaincc(self.statistic / 2, scale=self.nblocks / 2),
        ]
