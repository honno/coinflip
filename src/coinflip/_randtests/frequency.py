from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import erfc
from math import sqrt
from typing import Any
from typing import List
from typing import NamedTuple

import altair as alt
import numpy as np
import pandas as pd
from rich.text import Text
from scipy.special import gammaincc
from scipy.stats import halfnorm

from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_testvars_table
from coinflip._randtests.common.result import smartround
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.testutils import check_recommendations
from coinflip._randtests.common.testutils import randtest

__all__ = ["monobit", "frequency_within_block"]


# ------------------------------------------------------------------------------
# Frequency (Monobit) Test


class ValueCount(NamedTuple):
    value: Any
    count: int


class FaceCounts(NamedTuple):
    heads: ValueCount
    tails: ValueCount

    @property
    @lru_cache()
    def max(self):
        return max(*self, key=lambda value_count: value_count.count)

    @property
    @lru_cache()
    def min(self):
        return min(*self, key=lambda value_count: value_count.count)

    @classmethod
    def from_series(cls, series, heads, tails):
        heads = ValueCount(heads, series[heads])
        tails = ValueCount(tails, series[tails])
        return cls(heads, tails)


@randtest()
def monobit(series, heads, tails):
    n = len(series)

    check_recommendations({"n ≥ 100": n >= 100})

    counts = FaceCounts.from_series(series.value_counts(), heads, tails)

    diff = counts.max.count - counts.min.count
    normdiff = diff / sqrt(n)
    p = erfc(normdiff / sqrt(2))

    return MonobitTestResult(heads, tails, normdiff, p, n, counts, diff)


@dataclass
class MonobitTestResult(TestResult):
    n: int
    counts: FaceCounts
    diff: int

    def _render(self):
        yield self._pretty_result("normalised diff")

        counts = make_testvars_table("value", "count")
        counts.add_row(str(self.counts.max.value), str(self.counts.max.count))
        counts.add_row(str(self.counts.min.value), str(self.counts.min.count))
        yield counts

    def plot_counts(self):
        df = pd.DataFrame(
            {
                "Value": [self.counts.max.value, self.counts.min.value],
                "Count": [self.counts.max.count, self.counts.min.count],
            }
        )
        df["Value"] = df["Value"].astype("category")

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                alt.X("Value"),
                alt.Y("Count", axis=alt.Axis(tickMinStep=1)),
                tooltip=["Value", "Count"],
            )
            .properties(
                title=f"Counts of {self.counts.max.value} and {self.counts.min.value}"
            )
        )

        return chart

    def plot_refdist(self):
        mean = 0
        variance = 1
        deviation = sqrt(variance)

        xlim = max(4 * deviation, self.statistic + deviation)
        x = np.linspace(0, xlim)
        y = halfnorm.pdf(x, mean, deviation)
        x_stat = np.linspace(self.statistic, xlim)
        y_stat = halfnorm.pdf(x_stat, mean, deviation)

        dist = pd.DataFrame({"x": x, "y": y})
        dist_stat = pd.DataFrame({"x": x_stat, "y": y_stat})

        chart_dist = (
            alt.Chart(dist)
            .mark_area(opacity=0.3)
            .encode(
                alt.X(
                    "x", axis=alt.Axis(title="Difference between counts (normalised)")
                ),
                alt.Y(
                    "y",
                    axis=alt.Axis(title="Probability density"),
                    scale=alt.Scale(domain=(0, 1)),
                ),
            )
            .properties(title="Proability density of count differences")
        )
        chart_stat = alt.Chart(dist_stat).mark_area().encode(x="x", y="y",)
        chart = chart_dist + chart_stat

        return chart


# ------------------------------------------------------------------------------
# Frequency within Block Test


@randtest(min_n=8)
def frequency_within_block(series, heads, tails, blocksize=None):
    n = len(series)

    # TODO - smarter defaults
    #      - meet 0.01 * n recommendation
    if not blocksize:
        blocksize = 8

    nblocks = n // blocksize

    check_recommendations(
        {
            "n ≥ 100": n >= 100,
            "blocksize ≥ 20": blocksize >= 20,
            "blocksize > 0.01 * n": blocksize > 0.01 * n,
            "nblocks < 100": nblocks < 100,
        }
    )

    occurences = []
    for block in blocks(series, blocksize):
        matches = block == heads
        occur = matches.sum()
        occurences.append(occur)

    proportions = (count / blocksize for count in occurences)
    deviations = (prop - 1 / 2 for prop in proportions)

    statistic = 4 * blocksize * sum(x ** 2 for x in deviations)
    p = gammaincc(nblocks / 2, statistic / 2)

    return FrequencyWithinBlockTestResult(
        heads, tails, statistic, p, blocksize, nblocks, occurences,
    )


@dataclass
class FrequencyWithinBlockTestResult(TestResult):
    blocksize: int
    nblocks: int
    occurences: List[int]

    def _render(self):
        yield self._pretty_result("chi-square")

        occur_expect = self.blocksize / 2
        f_occur_expect = smartround(occur_expect)
        yield Text(f"expected occurences of {self.heads} per block: {f_occur_expect}")

        occur_counts = Counter(self.occurences)
        table = make_testvars_table("count", "nblocks")
        for occur, count in sorted(occur_counts.items()):
            table.add_row(str(occur), str(count))

        yield table

    # TODO delete this when jinja2 template and altair plotting methods are done
    # def _report(self):
    #     occurfig, occurax = plt.subplots()

    #     x_axis = [i * self.blocksize for i in range(len(self.occurences))]

    #     occurax.set_ylim([0, self.blocksize])
    #     occurax.bar(x_axis, self.occurences, width=self.blocksize * 0.9, align="edge")
    #     occurax.axhline(self.blocksize / 2, color="black")

    #     return [
    #         f"p={self.p3f()}",
    #         occurfig,
    #         plot_chi2(self.statistic, df=self.nblocks),
    #         plot_gammaincc(self.statistic / 2, self.nblocks / 2),
    #     ]
