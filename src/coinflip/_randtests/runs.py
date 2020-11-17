from dataclasses import astuple
from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import NamedTuple
from typing import Tuple

import altair as alt
import pandas as pd
from rich.text import Text
from scipy.stats import chisquare

from coinflip._randtests.common.collections import Bins
from coinflip._randtests.common.collections import FloorDict
from coinflip._randtests.common.core import *
from coinflip._randtests.common.exceptions import TestNotImplementedError
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_chisquare_table
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.typing import Float
from coinflip._randtests.common.typing import Integer

__all__ = ["runs", "longest_runs"]


# ------------------------------------------------------------------------------
# Runs Test


@randtest()
def runs(series, heads, tails, ctx):
    n = len(series)

    set_task_total(ctx, 4)

    failures = check_recommendations(ctx, {"n ≥ 100": n >= 100})

    counts = series.value_counts()

    advance_task(ctx)

    nheads = counts[heads]
    prop_heads = nheads / n
    prop_tails = 1 - prop_heads

    advance_task(ctx)

    nruns = sum(1 for _ in asruns(series))

    advance_task(ctx)

    p = erfc(
        abs(nruns - (2 * nheads * prop_tails))
        / (2 * sqrt(2 * n) * prop_heads * prop_tails)
    )

    advance_task(ctx)

    return RunsTestResult(heads, tails, failures, nruns, p)


@dataclass
class RunsTestResult(TestResult):
    def _render(self):
        yield self._pretty_result("no. of runs")


# ------------------------------------------------------------------------------
# Longest Runs in Block Test


class DefaultParams(NamedTuple):
    blocksize: Integer
    nblocks: Integer
    intervals: List[Integer]


# TODO use in recommendations
n_defaults = FloorDict(
    {
        128: DefaultParams(8, 16, [1, 2, 3, 4]),
        6272: DefaultParams(128, 49, [4, 5, 6, 7, 8, 9]),
        750000: DefaultParams(10 ** 4, 75, [10, 11, 12, 13, 14, 15, 16]),
    }
)


# TODO Work out a general solution (which is performative!)
blocksize_probabilities = {
    8: [0.2148, 0.3672, 0.2305, 0.1875],
    128: [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124],
    512: [0.1170, 0.2460, 0.2523, 0.1755, 0.1027, 0.1124],
    1000: [0.1307, 0.2437, 0.2452, 0.1714, 0.1002, 0.1088],
    10000: [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727],
}


# TODO allow and handle blocksize/nblocks/maxlen_bins kwargs
@randtest()
def longest_runs(series, heads, tails, ctx):
    n = len(series)

    try:
        blocksize, nblocks, intervals = n_defaults[n]
    except KeyError as e:
        # TODO handle below 128 or add to min_n
        raise TestNotImplementedError(
            "Test implementation cannot handle sequences below length 128"
        ) from e
    maxlen_bins = Bins(intervals)

    set_task_total(ctx, nblocks + 2)

    failures = check_recommendations(ctx, {"n ≥ 128": n >= 128})

    try:
        probabilities = blocksize_probabilities[blocksize]
    except KeyError as e:
        raise TestNotImplementedError(
            "Test implementation currently cannot calculate probabilities\n"
            f"Values are pre-calculated, which do not include blocksizes of {blocksize}"
        ) from e
    expected_bincounts = [prob * nblocks for prob in probabilities]

    advance_task(ctx)

    boundary = nblocks * blocksize
    for block in blocks(series[:boundary], blocksize):
        runlengths = (length for value, length in asruns(block) if value == heads)

        maxlen = 0
        for length in runlengths:
            if length > maxlen:
                maxlen = length

        maxlen_bins[maxlen] += 1

        advance_task(ctx)

    statistic, p = chisquare(list(maxlen_bins.values()), expected_bincounts)

    advance_task(ctx)

    return LongestRunsTestResult(
        heads,
        tails,
        failures,
        statistic,
        p,
        blocksize,
        nblocks,
        expected_bincounts,
        maxlen_bins,
    )


@dataclass
class LongestRunsTestResult(TestResult):
    blocksize: Integer
    nblocks: Integer
    expected_bincounts: List[Float]
    maxlen_bins: Dict[Integer, Integer]

    def _fmt_maxlen_ranges(self) -> List[str]:
        f_ranges = [str(x) for x in self.maxlen_bins.keys()]
        f_ranges[0] = f"0-{f_ranges[0]}"
        f_ranges[-1] = f"{f_ranges[-1]}+"

        return f_ranges

    def _render(self):
        yield self._pretty_result("chi-square")

        yield TestResult._pretty_inputs(
            ("blocksize", self.blocksize),
            ("nblocks", self.nblocks),
        )

        title = Text.assemble(
            "longest run of ", (str(self.heads), "bold"), " per block"
        )

        table = make_chisquare_table(
            title,
            "maxlen",
            self._fmt_maxlen_ranges(),
            self.expected_bincounts,
            self.maxlen_bins.values(),
        )

        yield table

    def plot_maxlen_bins(self):
        df = pd.DataFrame(
            {
                "Longest run": self._fmt_maxlen_ranges(),
                "Number of blocks": self.maxlen_bins.values(),
            }
        )

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                alt.X("Longest run", axis=alt.Axis(tickMinStep=1)),
                alt.Y("Number of blocks"),
                tooltip="Number of blocks",
            )
            .properties(title=f"Longest runs of {self.heads} per block")
        )

        return chart


# ------------------------------------------------------------------------------
# Helpers


@dataclass
class Run:
    value: Any
    length: Integer = 1


def asruns(series) -> Iterator[Tuple[Any, Integer]]:
    """Iterator of runs in a ``Series``

    Parameters
    ----------
    series: ``Series``
        ``Series`` to represent as runs

    Yields
    ------
    value : ``Any``
        Value of the run
    length : ``Integer``
        Length of the run

    Notes
    -----
    A "run" is an uninterrupted sequence of the same value.
    """
    firstval = series.iloc[0]
    current_run = Run(firstval, length=0)
    for _, value in series.items():
        if value == current_run.value:
            current_run.length += 1
        else:
            yield astuple(current_run)
            current_run = Run(value)

    yield astuple(current_run)
