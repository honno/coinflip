from dataclasses import dataclass
from math import ceil
from typing import Any

from click import echo


@dataclass
class ValueRepeats:
    value: Any
    repeats: int = 1


def runs(series):
    coded_series = []

    first_value = series.iloc[0]
    coded_series.append(ValueRepeats(first_value, repeats=0))

    for _, value in series.iteritems():
        tail = coded_series[-1]

        if value == tail.value:
            tail.repeats += 1
        else:
            coded_series.append(ValueRepeats(value))

    echo(coded_series[:5])

    # TODO summary statsticss


# TODO refactor block testing (i.e. frequency does this too)
def runs_in_block(series, block_size=None, nblocks=10):
    if block_size is None:
        block_size = ceil(len(series) / nblocks)

    while len(series) != 0:
        series_block, series = series[:block_size], series[block_size:]

        runs(series_block)

    # TODO summary statistics
