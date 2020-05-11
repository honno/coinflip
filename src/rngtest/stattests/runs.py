from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any

from scipy.special import gammaincc

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks


@binary_stattest
def runs(series, of_value=1):
    n = len(series)

    counts = series.value_counts()
    count_of_value = counts[of_value]
    proportion_of_value = counts[of_value] / n

    runs = as_runs(series)
    no_of_runs = sum(1 for _ in runs)

    p = erfc(
        abs(no_of_runs - (2 * count_of_value * (1 - proportion_of_value)))
        / (2 * sqrt(2 * n) * proportion_of_value * (1 - proportion_of_value))
    )

    return RunsTestResult(p=p, no_of_runs=no_of_runs)


@binary_stattest
def longest_runs(series, of_value=1):
    n = len(series)
    block_size, tally_range, K, N, probabilities = get_constants(n)

    longest_run_lengths = longest_run_per_block(series, of_value, block_size)
    coded_frequencies = tally_lengths(longest_run_lengths, tally_range)

    def partials():
        for prop, code in zip(probabilities, coded_frequencies):
            yield (code - N * prop) ** 2 / (N * prop)

    statistic = sum(partials())

    p = gammaincc(K / 2, statistic / 2)

    return LongestRunInBlockTestResult(p=p)


def tally_lengths(lengths, tally_range):
    def encode(length):
        lower = tally_range[0]
        if length <= lower:
            return 0

        for cell, code in enumerate(tally_range[1:-1], 1):
            if length == code:
                return cell

        upper = tally_range[-1]
        if length >= upper:
            return len(tally_range)

    cells = [0 for tally in tally_range]
    for length in lengths:
        code = encode(length)
        cells[code] += 1

    return cells


def longest_run_per_block(series, of_value, block_size):
    for chunk in chunks(series, block_size=block_size):
        runs = as_runs(chunk)
        of_value_runs = (run for run in runs if run.value == of_value)

        longest_run = 0
        for run in of_value_runs:
            if run.repeats > longest_run:
                longest_run = run.repeats

        yield longest_run


probability_constants = {
    8: [0.2148, 0.3672, 0.2305, 0.1875],
    128: [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124],
    512: [0.1170, 0.2460, 0.2523, 0.1755, 0.1027, 0.1124],
    1000: [0.1307, 0.2437, 0.2452, 0.1714, 0.1002, 0.1088],
    10000: [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727],
}


def get_constants(n):
    if n < 128:
        raise ValueError()
    elif n < 6272:
        block_size = 8
        tally_range = [1, 2, 3, 4]
        K = 3
        N = 16
    elif n < 750000:
        block_size = 128
        tally_range = [4, 5, 6, 7, 8, 9]
        K = 5
        N = 49
    else:
        block_size = 10 ** 4
        tally_range = [10, 11, 12, 13, 14, 15, 16]
        K = 6
        N = 75

    try:
        probabilities = probability_constants[block_size]
    except KeyError:
        raise ValueError()

    return block_size, tally_range, K, N, probabilities


@dataclass
class Run:
    value: Any
    repeats: int = 1


def as_runs(series):
    first_value = series.iloc[0]
    current_run = Run(first_value, repeats=0)
    for _, value in series.iteritems():
        if value == current_run.value:
            current_run.repeats += 1
        else:
            yield current_run

            current_run = Run(value)
    else:
        yield current_run


@dataclass
class RunsTestResult(TestResult):
    no_of_runs: int

    def __str__(self):
        return f"p={self.p2f()}"


class LongestRunInBlockTestResult(TestResult):
    pass
