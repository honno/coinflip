from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any

from scipy.special import gammaincc

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks
from rngtest.stattests.common import elected

__all__ = ["runs", "longest_runs"]


@binary_stattest
def runs(series, candidate=1):
    n = len(series)

    counts = series.value_counts()
    count_of_value = counts[candidate]
    proportion_of_value = counts[candidate] / n

    runs = as_runs(series)
    no_of_runs = sum(1 for _ in runs)

    p = erfc(
        abs(no_of_runs - (2 * count_of_value * (1 - proportion_of_value)))
        / (2 * sqrt(2 * n) * proportion_of_value * (1 - proportion_of_value))
    )

    return RunsTestResult(statistic=no_of_runs, p=p)


@elected
@binary_stattest
def longest_runs(series, candidate=None):
    n = len(series)

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

    probability_constants = {
        8: [0.2148, 0.3672, 0.2305, 0.1875],
        128: [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124],
        512: [0.1170, 0.2460, 0.2523, 0.1755, 0.1027, 0.1124],
        1000: [0.1307, 0.2437, 0.2452, 0.1714, 0.1002, 0.1088],
        10000: [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727],
    }
    try:
        probabilities = probability_constants[block_size]
    except KeyError:
        raise ValueError()

    longest_run_lengths = []
    for chunk in chunks(series, block_size=block_size):
        runs = as_runs(chunk)
        of_value_runs = (run for run in runs if run.value == candidate)

        longest_run = 0
        for run in of_value_runs:
            if run.repeats > longest_run:
                longest_run = run.repeats

        longest_run_lengths.append(longest_run)

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

    coded_frequencies = [0 for tally in tally_range]
    for length in longest_run_lengths:
        code = encode(length)
        coded_frequencies[code] += 1

    statistic_partials = []
    for prop, code in zip(probabilities, coded_frequencies):
        partial = (code - N * prop) ** 2 / (N * prop)
        statistic_partials.append(partial)

    statistic = sum(statistic_partials)
    p = gammaincc(K / 2, statistic / 2)

    return TestResult(statistic=statistic, p=p)


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
    def __str__(self):
        return f"p={self.p3f()}"

    def _report(self):
        return [f"p={self.p3f()}"]
