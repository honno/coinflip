from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any
from typing import List
from typing import NamedTuple

from scipy.special import gammaincc

from rngtest.stattests._common import FloorDict
from rngtest.stattests._common import TestResult
from rngtest.stattests._common import chunks
from rngtest.stattests._common import elected
from rngtest.stattests._common import stattest

__all__ = ["runs", "longest_runs"]


@stattest
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


# TODO allow and handle blocksize/nblocks/freqbinranges kwargs
@stattest
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
    blocksize, nblocks, freqbinranges = n_defaults[n]

    def freqbin(runlength):
        minlen = freqbinranges[0]
        midlengths = freqbinranges[1:-1]
        maxlen = freqbinranges[-1]

        if runlength <= minlen:
            return 0

        elif minlen < runlength < maxlen:
            for freqbin, length in enumerate(midlengths, 1):
                if runlength == length:
                    return freqbin

        elif runlength >= maxlen:
            maxbin = len(freqbinranges) - 1
            return maxbin

    df = len(freqbinranges) - 1

    try:
        maxlen_probabilities = blocksize_probabilities[blocksize]
    except KeyError:
        raise NotImplementedError()

    # --------------------------------------------------------------------------
    # Test logic

    maxlengths = []
    for chunk in chunks(series, blocksize=blocksize):
        candidateruns = (run for run in asruns(chunk) if run.value == candidate)

        maxlen = 0
        for run in candidateruns:
            if run.length > maxlen:
                maxlen = run.length

        maxlengths.append(maxlen)

    freqbins = [0 for _ in freqbinranges]
    for runlength in maxlengths:
        freqbins[freqbin(runlength)] += 1

    partials = []
    for prob, bincount in zip(maxlen_probabilities, freqbins):
        partial = (bincount - nblocks * prob) ** 2 / (nblocks * prob)
        partials.append(partial)

    statistic = sum(partials)
    p = gammaincc(df / 2, statistic / 2)

    return TestResult(statistic=statistic, p=p)


# ------------------------------------------------------------------------------
# Components used in longest_runs


class DefaultParams(NamedTuple):
    blocksize: int
    nblocks: int
    freqbinranges: List[int]


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


# ------------------------------------------------------------------------------
# asruns helper method


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


# ------------------------------------------------------------------------------
# Results


@dataclass
class RunsTestResult(TestResult):
    def __str__(self):
        return f"p={self.p3f()}\n" f"Sequence held {self.statistic} number of runs\n"
