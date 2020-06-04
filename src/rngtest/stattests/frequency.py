from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any
from typing import List
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.special import gammaincc
from scipy.stats import halfnorm

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks
from rngtest.stattests.common import elected
from rngtest.stattests.common import plot_chi2
from rngtest.stattests.common import plot_gammaincc
from rngtest.stattests.common import range_annotation

__all__ = ["monobits", "frequency_within_block"]


@binary_stattest
def monobits(series):
    counts = series.value_counts()

    n = len(series)
    difference = abs(counts.iloc[0] - counts.iloc[1])
    statistic = difference / sqrt(n)
    p = erfc(statistic / sqrt(2))

    return MonobitsTestResult(
        statistic=statistic, p=p, n=n, difference=difference, counts=counts
    )


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
    n: int
    difference: int

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
            self.plot_counts(),
            self.plot_reference_dist(),
        ]

    def plot_counts(self):
        ax = self.counts.plot.bar(rot=0)
        fig = ax.get_figure()

        ax.set_title(f"Occurences of {self.mincount.value} and {self.maxcount.value}")
        ax.set_xlabel("Values")
        ax.set_ylabel("No. of occurences")

        ax.axhline(self.maxcount.count, color="black", linestyle="--")

        margin = 0.1
        plt.annotate(
            s="",
            xy=(1, self.mincount.count + margin),
            xytext=(1, self.maxcount.count - margin),
            arrowprops=dict(arrowstyle="<->"),
        )

        ax.text(
            1 - margin,
            self.mincount.count + 1 / 2 * self.difference,
            f"difference = {self.difference}",
            ha="right",
        )

        return fig

    def plot_reference_dist(self):
        fig, ax = plt.subplots()

        ax.set_title("Probability densities for differences")
        ax.set_xlabel("Difference between occurences (normalised)")
        ax.set_ylabel("Probability density")

        # ------------------------
        # Half-normal distribution
        # ------------------------

        mean = 0
        variance = 1
        deviation = sqrt(variance)

        xlim = max(3 * deviation, self.statistic)
        x = np.linspace(0, xlim)
        y = halfnorm.pdf(x, mean, deviation)

        ax.plot(x, y, color="black")

        # ------------
        # p-value area
        # ------------

        fill_x = x[x > self.statistic]
        fill_y = y[-len(fill_x) :]

        # Add self.statistic point to plot fill area from its boundary
        fill_x = np.insert(fill_x, 0, self.statistic)
        statistic_pdf = halfnorm.pdf(self.statistic, mean, deviation)
        fill_y = np.insert(fill_y, 0, statistic_pdf)

        ax.fill_between(
            fill_x, 0, fill_y, facecolor="none", hatch="//", edgecolor="black"
        )

        # -----------
        # Annotations
        # -----------

        ax.set_ylim([0, 1])
        stat2f = round(self.statistic, 2)
        annotation_text = (
            "area under curve represents the\n"
            "probability that a truly random sample would\n"
            f"at least have a normalised difference of {stat2f}"
        )
        range_annotation(
            ax=ax, xmin=self.statistic, xmax=xlim, ymin=fill_y[0], text=annotation_text
        )

        probability = "{:.1%}".format(self.p)
        ax.text(xlim, fill_y[0] / 2, f"probability = {probability}", ha="right")

        return fig


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
