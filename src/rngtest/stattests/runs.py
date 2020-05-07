from dataclasses import dataclass
from math import ceil
from typing import Any


def longest_runs(series, block_size=None, nblocks=10, of_value=None):
    if series.nunique() != 2:
        raise NotImplementedError()

    if block_size is None:
        block_size = ceil(len(series) / nblocks)

    if of_value is None:
        of_value = series.unique()[0]
    else:
        if of_value not in series:
            raise ValueError(f"of_value '{of_value}' not found in sequence")

    longest_run_per_block = []
    while len(series) != 0:
        series_block, series = series[:block_size], series[block_size:]

        longest_run_length = 0
        for run in as_runs(series_block):
            if run.value == of_value:
                if run.repeats > longest_run_length:
                    longest_run = run.repeats

        longest_run_per_block.append(longest_run)

    raise NotImplementedError()


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


# TODO refactor block testing (i.e. frequency does this too)
# def runs_in_block(series, block_size=None, nblocks=10):
#     if block_size is None:
#         block_size = ceil(len(series) / nblocks)

#     while len(series) != 0:
#         series_block, series = series[:block_size], series[block_size:]

#         runs(series_block)
