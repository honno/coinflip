from collections import defaultdict
from math import floor
from math import log2

import pandas as pd
from scipy.special import gammaincc

from coinflip.randtests._decorators import randtest
from coinflip.randtests._result import MultiTestResult
from coinflip.randtests._result import TestResult
from coinflip.randtests._testutils import check_recommendations
from coinflip.randtests._testutils import slider

__all__ = ["serial"]


@randtest()
def serial(series, blocksize=None):
    n = len(series)

    if not blocksize:
        blocksize = floor(log2(n)) - 2 - 1

    check_recommendations({"blocksize < ⌊log2(n) - 2⌋": blocksize < floor(log2(n)) - 2})

    normalised_sums = {}
    for window_size in [blocksize, blocksize - 1, blocksize - 2]:
        head = series[: window_size - 1]
        ouroboros = pd.concat([series, head])

        permutation_counts = defaultdict(int)
        for block_tup in slider(ouroboros, window_size, overlap=True):
            permutation_counts[block_tup] += 1

        sum_squares = sum(count ** 2 for count in permutation_counts.values())
        normsum = (2 ** window_size / n) * sum_squares - n

        normalised_sums[window_size] = normsum

    normsum_delta1 = normalised_sums[blocksize] - normalised_sums[blocksize - 1]
    normsum_delta2 = (
        normalised_sums[blocksize]
        - 2 * normalised_sums[blocksize - 1]
        + normalised_sums[blocksize - 2]
    )

    p1 = gammaincc(2 ** (blocksize - 2), normsum_delta1 / 2)
    p2 = gammaincc(2 ** (blocksize - 3), normsum_delta2 / 2)

    results = {
        1: SerialTestResult(normsum_delta1, p1),
        2: SerialTestResult(normsum_delta2, p2),
    }

    return MultiSerialTestResult(results)


class SerialTestResult(TestResult):
    def __rich_console__(self, console, options):
        yield self._results_text("chi-square")


class MultiSerialTestResult(MultiTestResult):
    def __rich_console__(self, console, options):
        yield "First"
        yield self[1]
        yield ""
        yield "Second"
        yield self[2]
