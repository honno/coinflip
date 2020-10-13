from dataclasses import astuple
from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any
from typing import Iterator
from typing import List
from typing import NamedTuple
from typing import Tuple

from scipy.special import gammaincc

from coinflip._randtests.common.collections import Bins
from coinflip._randtests.common.collections import FloorDict
from coinflip._randtests.common.exceptions import TestNotImplementedError
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_reality_check_table
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.testutils import check_recommendations
from coinflip._randtests.common.testutils import randtest

__all__ = ["runs", "longest_runs"]


# ------------------------------------------------------------------------------
# Runs Test


@randtest()
def runs(series, heads, tails):
    n = len(series)

    check_recommendations({"n ≥ 100": n >= 100})

    counts = series.value_counts()

    ncandidates = counts[heads]
    prop_heads = ncandidates / n
    prop_tails = 1 - prop_heads

    nruns = sum(1 for _ in asruns(series))

    p = erfc(
        abs(nruns - (2 * ncandidates * prop_tails))
        / (2 * sqrt(2 * n) * prop_heads * prop_tails)
    )

    return RunsTestResult(heads, tails, nruns, p)


@dataclass
class RunsTestResult(TestResult):
    def __rich_console__(self, console, options):
        yield self._results_text("no. of runs")


# ------------------------------------------------------------------------------
# Longest Runs in Block Test


class DefaultParams(NamedTuple):
    blocksize: int
    nblocks: int
    maxlen_bin_intervals: List[int]


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
def longest_runs(series, heads, tails):
    n = len(series)

    check_recommendations({"n ≥ 128": n >= 128})

    try:
        blocksize, nblocks, maxlen_bin_intervals = n_defaults[n]
    except KeyError as e:
        # TODO handle below 128 or add to min_n
        raise TestNotImplementedError(
            "Test implementation cannot handle sequences below length 128"
        ) from e
    df = len(maxlen_bin_intervals) - 1
    maxlen_bins = Bins(maxlen_bin_intervals)

    try:
        maxlen_probs = blocksize_probabilities[blocksize]
    except KeyError as e:
        raise TestNotImplementedError(
            "Test implementation currently cannot calculate probabilities\n"
            f"Values are pre-calculated, which do not include blocksizes of {blocksize}"
        ) from e
    expected_bincounts = [prob * nblocks for prob in maxlen_probs]

    for block in blocks(series, blocksize, nblocks=nblocks):
        runlengths = (length for value, length in asruns(block) if value == heads)

        maxlen = 0
        for length in runlengths:
            if length > maxlen:
                maxlen = length

        maxlen_bins[maxlen] += 1

    reality_check = []
    bincounts = maxlen_bins.values()
    for count_expect, count in zip(expected_bincounts, bincounts):
        diff = (count - count_expect) ** 2 / count_expect
        reality_check.append(diff)

    statistic = sum(reality_check)
    p = gammaincc(df / 2, statistic / 2)

    return LongestRunsTestResult(
        heads, tails, statistic, p, blocksize, nblocks, expected_bincounts, maxlen_bins,
    )


@dataclass
class LongestRunsTestResult(TestResult):
    blocksize: int
    nblocks: int
    expected_bincounts: List[float]
    maxlen_bins: Bins

    def __rich_console__(self, console, options):
        yield self._results_text("chi-square")

        f_ranges = [str(x) for x in self.maxlen_bins.keys()]
        f_ranges[0] = f"0-{f_ranges[0]}"
        f_ranges[-1] = f"{f_ranges[-1]}+"

        table = make_reality_check_table(
            "maxlen", f_ranges, self.expected_bincounts, self.maxlen_bins.values(),
        )

        yield table


# ------------------------------------------------------------------------------
# Helpers


@dataclass
class Run:
    value: Any
    length: int = 1


def asruns(series) -> Iterator[Tuple[Any, int]]:
    """Iterator of runs in a ``Series``

    Parameters
    ----------
    series: ``Series``
        ``Series`` to represent as runs

    Yields
    ------
    value : ``Any``
        Value of the run
    length : ``int``
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
    else:
        yield astuple(current_run)
