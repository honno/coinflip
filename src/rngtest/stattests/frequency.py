from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any
from typing import NamedTuple

import pandas as pd
from scipy.special import gammaincc

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks
from rngtest.stattests.common import stattest


@stattest
def frequency(series):
    counts = series.value_counts()

    return FrequencyTestResult(p=None, counts=counts)


@binary_stattest
def monobits(series):
    counts = series.value_counts()

    n = len(series)
    difference = counts.iloc[0] - counts.iloc[1]
    statistic = abs(difference) / sqrt(n)
    p = erfc(statistic / sqrt(2))

    return MonobitsTestResult(p=p, counts=counts)


@binary_stattest
def frequency_within_block(series, of_value=1, block_size=8):
    if len(series) < 100:
        raise ValueError()

    nblocks = len(series) // block_size
    proportions = proportions_of_value_per_block(series, of_value, block_size)
    deviations = deviations_from_uniform_distribution(proportions)
    statistic = 4 * block_size * sum(x ** 2 for x in deviations)

    p = gammaincc(nblocks / 2, statistic / 2)

    return FrequencyWithinBlocksTest(p=p)


def proportions_of_value_per_block(series, of_value, block_size):
    for chunk in chunks(series, block_size=block_size):
        counts = chunk.value_counts()
        try:
            freq = counts[of_value]
            proportion_of_value = freq / block_size

            yield proportion_of_value

        except KeyError:

            yield 0


def deviations_from_uniform_distribution(proportions):
    for prop in proportions:
        deviation = prop - 1 / 2

        yield deviation


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


class MonobitsTestResult(BaseFrequencyTestResult):
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


class FrequencyWithinBlocksTest(TestResult):
    pass
