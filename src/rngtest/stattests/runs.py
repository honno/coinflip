from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Any

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest


@binary_stattest
def runs(series, of_value=1):
    n = len(series)

    counts = series.value_counts()
    count_of_value = counts[of_value]
    proportion_of_value = counts[of_value] / n

    runs = as_runs(series)
    no_of_runs = sum(1 for _ in runs)
    statistic = no_of_runs + 1

    p = erfc(
        (statistic - (2 * count_of_value * (1 - proportion_of_value)))
        / (2 * sqrt(2 * n) * proportion_of_value * (1 - proportion_of_value))
    )

    return RunsTestResult(p=p)


# def longest_runs(series, block_size=None, nblocks=10, of_value=None):
#     if series.nunique() != 2:
#         raise NotImplementedError()

#     if block_size is None:
#         block_size = ceil(len(series) / nblocks)

#     if of_value is None:
#         of_value = series.unique()[0]
#     else:
#         if of_value not in series:
#             raise ValueError(f"of_value '{of_value}' not found in sequence")

#     longest_run_per_block = []
#     while len(series) != 0:
#         series_block, series = series[:block_size], series[block_size:]

#         longest_run_length = 0
#         for run in as_runs(series_block):
#             if run.value == of_value:
#                 if run.repeats > longest_run_length:
#                     longest_run = run.repeats

#         longest_run_per_block.append(longest_run)

#     raise NotImplementedError()


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


@dataclass
class RunsTestResult(TestResult):
    def __str__(self):
        return f"p={self.p2f()}"


# TODO refactor block testing (i.e. frequency does this too)
# def runs_in_block(series, block_size=None, nblocks=10):
#     if block_size is None:
#         block_size = ceil(len(series) / nblocks)

#     while len(series) != 0:
#         series_block, series = series[:block_size], series[block_size:]

#         runs(series_block)
