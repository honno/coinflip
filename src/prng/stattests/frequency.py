from math import ceil

from click import echo


def frequency(series):
    counts = series.value_counts()

    echo(counts.head())

    # TODO summary statistics


def frequency_in_block(series, block_size=None, nblocks=10):
    if block_size is None:
        block_size = ceil(len(series) / nblocks)

    while len(series) != 0:
        series_block, series = series[:block_size], series[block_size:]

        frequency(series_block)

    # TODO summary statistics
