from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any
from typing import List
from typing import NamedTuple

from scipy.special import gammaincc
from tabulate import tabulate

from rngtest.stattests._common import FloorDict
from rngtest.stattests._common import TestResult
from rngtest.stattests._common import blocks
from rngtest.stattests._common import elected
from rngtest.stattests._common import stattest

__all__ = ["runs", "longest_runs"]


# ------------------------------------------------------------------------------
# Runs Test


@stattest()
@elected
def runs(series, candidate):
    """Actual number of runs is compared to expected result

    The number of runs (uninterrupted sequence of the same value) is found, and
    referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    candidate : Value present in given series
        The value which is counted in each block

    Returns
    -------
    TestResult
        Dataclass that contains the test's statistic and p-value
    """
    n = len(series)

    counts = series.value_counts()

    ncandidates = counts[candidate]
    prop_candidates = ncandidates / n
    prop_noncandidates = 1 - prop_candidates

    nruns = sum(1 for _ in asruns(series))

    p = erfc(
        abs(nruns - (2 * ncandidates * prop_noncandidates))
        / (2 * sqrt(2 * n) * prop_candidates * prop_noncandidates)
    )

    return RunsTestResult(statistic=nruns, p=p)


@dataclass
class RunsTestResult(TestResult):
    def __str__(self):
        return self.stats_table("no. of runs")


# ------------------------------------------------------------------------------
# Longest Runs in Block Test


class DefaultParams(NamedTuple):
    blocksize: int
    nblocks: int
    freqbin_ranges: List[int]


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


# TODO allow and handle blocksize/nblocks/freqbin_ranges kwargs
@stattest(min_input=128)
@elected
def longest_runs(series, candidate):
    """Longest runs per block is compared to expected result

    The longest number of runs (uninterrupted sequence of the same value) per
    block is found, and referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    candidate : Value present in given series
        The value which is counted in each block

    Returns
    -------
    TestResult
        Dataclass that contains the test's statistic and p-value
    """

    # --------------------------------------------------------------------------
    # Finding test constants

    n = len(series)
    blocksize, nblocks, freqbin_ranges = n_defaults[n]

    # TODO range list
    def freqbin(runlength):
        minlen = freqbin_ranges[0]
        midlengths = freqbin_ranges[1:-1]
        maxlen = freqbin_ranges[-1]

        if runlength <= minlen:
            return 0

        elif minlen < runlength < maxlen:
            for freqbin, length in enumerate(midlengths, 1):
                if runlength == length:
                    return freqbin

        elif runlength >= maxlen:
            maxbin = len(freqbin_ranges) - 1
            return maxbin

    df = len(freqbin_ranges) - 1

    try:
        maxlen_probs = blocksize_probabilities[blocksize]
    except KeyError:
        raise NotImplementedError()
    freqbins_expect = [prob * nblocks for prob in maxlen_probs]

    # --------------------------------------------------------------------------
    # Test logic

    maxlengths = []
    for block in blocks(series, blocksize=blocksize, nblocks=nblocks):
        candidateruns = (run for run in asruns(block) if run.value == candidate)

        maxlen = 0
        for run in candidateruns:
            if run.length > maxlen:
                maxlen = run.length

        maxlengths.append(maxlen)

    freqbins = [0 for _ in freqbin_ranges]
    for runlength in maxlengths:
        freqbins[freqbin(runlength)] += 1

    reality_check = []
    for count_expect, count in zip(freqbins_expect, freqbins):
        diff = (count - count_expect) ** 2 / count_expect
        reality_check.append(diff)

    statistic = sum(reality_check)
    p = gammaincc(df / 2, statistic / 2)

    return LongestRunsTestResult(
        statistic=statistic,
        p=p,
        candidate=candidate,
        blocksize=blocksize,
        nblocks=nblocks,
        freqbin_ranges=freqbin_ranges,
        freqbins_expect=freqbins_expect,
        freqbins=freqbins,
    )


@dataclass
class LongestRunsTestResult(TestResult):
    candidate: Any
    blocksize: int
    nblocks: int
    freqbin_ranges: List[int]
    freqbins_expect: List[float]
    freqbins: List[int]

    def __post_init__(self):
        self.freqbin_diffs = []
        for expected, actual in zip(self.freqbins_expect, self.freqbins):
            diff = expected - actual
            self.freqbin_diffs.append(diff)

    def __str__(self):
        f_stats = self.stats_table("chi-square")

        f_ranges = [str(x) for x in self.freqbin_ranges]
        f_ranges[0] = f"0-{f_ranges[0]}"
        f_ranges[-1] = f"{f_ranges[-1]}+"

        f_expect = [round(count, 1) for count in self.freqbins_expect]

        f_diffs = [round(diff, 1) for diff in self.freqbin_diffs]

        ftable = tabulate(
            zip(f_ranges, self.freqbins, f_expect, f_diffs),
            ["maxlen", "nblocks", "expected", "diff"],
        )

        return f"{f_stats}\n" "\n" f"{ftable}"


# ------------------------------------------------------------------------------
# Helpers


@dataclass
class Run:
    value: Any
    length: int = 1


def asruns(series):
    firstval = series.iloc[0]
    current_run = Run(firstval, length=0)
    for _, value in series.iteritems():
        if value == current_run.value:
            current_run.length += 1
        else:
            yield current_run
            current_run = Run(value)
    else:
        yield current_run
