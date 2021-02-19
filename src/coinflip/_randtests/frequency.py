from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import erfc
from math import sqrt
from operator import attrgetter
from typing import List
from typing import NamedTuple

import altair as alt
import pandas as pd
from rich.text import Text
from scipy.special import gammaincc

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_testvars_table
from coinflip._randtests.common.result import plot_chi2_dist
from coinflip._randtests.common.result import plot_halfnorm_dist
from coinflip._randtests.common.result import smartround
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.typing import Face
from coinflip._randtests.common.typing import Integer

__all__ = ["monobit", "frequency_within_block"]


# ------------------------------------------------------------------------------
# Frequency (Monobit) Test


class FaceCount(NamedTuple):
    value: Face
    count: Integer


class FaceCounts(NamedTuple):
    heads: FaceCount
    tails: FaceCount

    @property
    @lru_cache()
    def max(self):
        return max(*self, key=attrgetter("count"))

    @property
    @lru_cache()
    def min(self):
        return min(*self, key=attrgetter("count"))

    @classmethod
    def from_series(cls, series, heads, tails):
        heads = FaceCount(heads, series[heads])
        tails = FaceCount(tails, series[tails])
        return cls(heads, tails)


@randtest()
def monobit(series, heads, tails, ctx):
    n = len(series)

    set_task_total(ctx, 2)

    failures = check_recommendations(ctx, {"n ≥ 100": n >= 100})

    counts = FaceCounts.from_series(series.value_counts(), heads, tails)

    advance_task(ctx)

    diff = counts.max.count - counts.min.count
    normdiff = diff / sqrt(n)
    p = erfc(normdiff / sqrt(2))

    advance_task(ctx)

    return MonobitTestResult(heads, tails, failures, normdiff, p, n, counts, diff)


@dataclass
class MonobitTestResult(TestResult):
    n: Integer
    counts: FaceCounts
    diff: Integer

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
                tooltip="Count",
            )
            .properties(
                title=f"Counts of {self.counts.max.value} and {self.counts.min.value}"
            )
        )

        return chart

    def plot_refdist(self):
        return plot_halfnorm_dist(
            self.statistic, xtitle="Difference between counts (normalised)"
        )


# ------------------------------------------------------------------------------
# Frequency within Block Test


@randtest(min_n=8)
def frequency_within_block(series, heads, tails, ctx, blocksize=None):
    n = len(series)

    # TODO - smarter defaults
    #      - meet 0.01 * n recommendation
    if not blocksize:
        blocksize = 8

    nblocks = n // blocksize

    set_task_total(ctx, nblocks + 3)

    failures = check_recommendations(
        ctx,
        {
            "n ≥ 100": n >= 100,
            "blocksize ≥ 20": blocksize >= 20,
            "blocksize > 0.01 * n": blocksize > 0.01 * n,
            "nblocks < 100": nblocks < 100,
        },
    )

    advance_task(ctx)

    counts = []
    for block in blocks(series, blocksize):
        matches = block == heads
        count = matches.sum()
        counts.append(count)

        advance_task(ctx)

    proportions = (count / blocksize for count in counts)
    deviations = [prop - 1 / 2 for prop in proportions]

    advance_task(ctx)

    # TODO figure out the chi-square test being used
    statistic = 4 * blocksize * sum(x ** 2 for x in deviations)
    p = gammaincc(nblocks / 2, statistic / 2)

    advance_task(ctx)

    return FrequencyWithinBlockTestResult(
        heads,
        tails,
        failures,
        statistic,
        p,
        blocksize,
        nblocks,
        counts,
    )


@dataclass
class FrequencyWithinBlockTestResult(TestResult):
    blocksize: Integer
    nblocks: Integer
    counts: List[Integer]

    def __post_init__(self):
        self.count_nblocks = Counter(self.counts)

    def _render(self):
        yield self._pretty_result("chi-square")

        yield TestResult._pretty_inputs(
            ("blocksize", self.blocksize), ("nblocks", self.nblocks)
        )

        title = Text.assemble("count of ", (str(self.heads), "bold"), " per block")

        count_expect = self.blocksize / 2
        f_count_expect = smartround(count_expect)
        caption = f"expected count {f_count_expect}"

        table = make_testvars_table("count", "nblocks", title=title, caption=caption)
        for count in range(self.blocksize + 1):
            nblocks = self.count_nblocks[count]
            table.add_row(str(count), str(nblocks))

        yield table

    def plot_count_nblocks(self):
        counts = range(self.blocksize + 1)
        df = pd.DataFrame(
            {
                "count": counts,
                "nblocks": [self.count_nblocks[count] for count in counts],
            }
        )

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                alt.X(
                    "count:O",
                    title=f"Count of {self.heads}",
                ),
                alt.Y(
                    "nblocks:Q",
                    title="Number of blocks",
                ),
            )
            .properties(title=f"Occurences of {self.heads} counts")
        )

        return chart

    def plot_refdist(self):
        return plot_chi2_dist(self.statistic, self.nblocks)
