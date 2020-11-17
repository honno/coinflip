from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from math import erfc
from math import sqrt
from operator import attrgetter
from typing import List
from typing import NamedTuple

import altair as alt
import numpy as np
import pandas as pd
from rich.text import Text
from scipy.special import gammaincc
from scipy.stats import halfnorm

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_testvars_table
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
        chart_stat = (
            alt.Chart(dist_stat)
            .mark_area()
            .encode(
                x="x",
                y="y",
            )
        )
        chart = chart_dist + chart_stat

        return chart


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

    def _render(self):
        yield self._pretty_result("chi-square")

        yield TestResult._pretty_inputs(
            ("blocksize", self.blocksize), ("nblocks", self.nblocks)
        )

        title = Text.assemble("count of ", (str(self.heads), "bold"), " per block")

        count_expect = self.blocksize / 2
        f_count_expect = smartround(count_expect)
        caption = f"expected count {f_count_expect}"

        count_nblocks = Counter(self.counts)
        table = make_testvars_table("count", "nblocks", title=title, caption=caption)
        for count in range(self.blocksize + 1):
            nblocks = count_nblocks[count]
            table.add_row(str(count), str(nblocks))

        yield table

    # TODO delete this when jinja2 template and altair plotting methods are done
    # def _report(self):
    #     occurfig, occurax = plt.subplots()

    #     x_axis = [i * self.blocksize for i in range(len(self.counts))]

    #     occurax.set_ylim([0, self.blocksize])
    #     occurax.bar(x_axis, self.counts, width=self.blocksize * 0.9, align="edge")
    #     occurax.axhline(self.blocksize / 2, color="black")

    #     return [
    #         f"p={self.p3f()}",
    #         occurfig,
    #         plot_chi2(self.statistic, df=self.nblocks),
    #         plot_gammaincc(self.statistic / 2, self.nblocks / 2),
    #     ]
