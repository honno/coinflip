from collections import Counter
from dataclasses import dataclass
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

from coinflip.randtests._decorators import elected
from coinflip.randtests._decorators import randtest
from coinflip.randtests._result import TestResult
from coinflip.randtests._result import make_testvars_table
from coinflip.randtests._result import smartround
from coinflip.randtests._testutils import blocks
from coinflip.randtests._testutils import check_recommendations

__all__ = ["monobit", "frequency_within_block"]


# ------------------------------------------------------------------------------
# Frequency (Monobit) Test


@randtest(rec_input=100)
def monobit(series):
    """Proportion of values is compared to expected 1:1 ratio

    The difference between the frequency of the two values is found, and
    referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested

    Returns
    -------
    MonobitTestResult
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """

    counts = series.value_counts()

    n = len(series)
    diff = abs(counts.iloc[0] - counts.iloc[1])
    normdiff = diff / sqrt(n)
    p = erfc(normdiff / sqrt(2))

    return MonobitTestResult(statistic=normdiff, p=p, n=n, diff=diff, counts=counts)


class ValueCount(NamedTuple):
    value: Any
    count: int


@dataclass
class MonobitTestResult(TestResult):
    counts: pd.Series
    n: int
    diff: int

    def __post_init__(self):
        self.maxcount = ValueCount(
            value=self.counts.index.values[0], count=self.counts.values[0]
        )
        self.mincount = ValueCount(
            value=self.counts.index.values[-1], count=self.counts.values[-1]
        )

    def __rich_console__(self, console, options):
        yield self._results_text("normalised diff")

        counts = make_testvars_table("value", "count")
        counts.add_row(str(self.maxcount.value), str(self.maxcount.count))
        counts.add_row(str(self.mincount.value), str(self.mincount.count))
        yield counts

    def plot_counts(self):
        df = pd.DataFrame(
            {
                "Value": [self.maxcount.value, self.mincount.value],
                "Count": [self.maxcount.count, self.mincount.count],
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
                title=f"Counts of {self.maxcount.value} and {self.mincount.value}"
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


@randtest(min_input=8, rec_input=100)
@elected
def frequency_within_block(series, candidate, blocksize=8):
    """Proportion of values per block is compared to expected 1:1 ratio

    The difference between the frequency of the two values in each block is
    found, and referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    candidate : Value present in given sequence
        The value which is counted in each block
    blocksize : `int`
        Size of the blocks that partition the given series

    Returns
    -------
    FrequencyWithinBlockTestResult
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    """
    n = len(series)
    nblocks = n // blocksize  # TODO meet 0.01 * n recommendation

    check_recommendations(
        {
            "blocksize ≥ 20": blocksize >= 20,
            "blocksize > 0.01 * n": blocksize > 0.01 * n,
            "nblocks < 100": nblocks < 100,
        }
    )

    occurences = []
    for block in blocks(series, blocksize=blocksize):
        matches = block == candidate
        occur = matches.sum()
        occurences.append(occur)

    proportions = (count / blocksize for count in occurences)
    deviations = (prop - 1 / 2 for prop in proportions)

    statistic = 4 * blocksize * sum(x ** 2 for x in deviations)
    p = gammaincc(nblocks / 2, statistic / 2)

    return FrequencyWithinBlockTestResult(
        statistic=statistic,
        p=p,
        candidate=candidate,
        blocksize=blocksize,
        nblocks=nblocks,
        occurences=occurences,
    )


@dataclass
class FrequencyWithinBlockTestResult(TestResult):
    candidate: Any
    blocksize: int
    nblocks: int
    occurences: List[int]

    def __rich_console__(self, console, options):
        yield self._results_text("chi-square")

        yield ""

        occur_expect = self.blocksize / 2
        f_occur_expect = smartround(occur_expect)
        yield Text(f"expected occurences per block: {f_occur_expect}")

        occur_counts = Counter(self.occurences)
        testvars = make_testvars_table("occur", "count")
        for occur, count in sorted(occur_counts.items()):
            testvars.add_row(str(occur), str(count))
        yield testvars

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
