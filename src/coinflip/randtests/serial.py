from collections import defaultdict
from dataclasses import dataclass
from math import floor
from math import log2
from typing import Tuple

import pandas as pd
from scipy.special import gammaincc

from coinflip.randtests._decorators import randtest
from coinflip.randtests._result import MultiTestResult
from coinflip.randtests._testutils import check_recommendations
from coinflip.randtests._testutils import slider

__all__ = ["serial"]


@randtest()
def serial(series, blocksize):
    n = len(series)

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

    return SerialTestResult((normsum_delta1, p1), (normsum_delta2, p2))


@dataclass
class SerialTestResult(MultiTestResult):
    result1: Tuple[float, float]
    result2: Tuple[float, float]

    @property
    def statistics(self):
        return [self.result1[0], self.result2[0]]

    @property
    def pvalues(self):
        return [self.result1[1], self.result2[1]]
