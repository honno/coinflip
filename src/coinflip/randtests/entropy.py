from collections import defaultdict
from math import log

import pandas as pd
from scipy.special import gammaincc

from coinflip.randtests._decorators import randtest
from coinflip.randtests._result import TestResult
from coinflip.randtests._testutils import rawslider

__all__ = ["approximate_entropy"]


@randtest()
def approximate_entropy(series, blocksize):
    n = len(series)

    totals = []
    for template_size in [blocksize, blocksize + 1]:
        head = series[: template_size - 1]
        ouroboros = pd.concat([series, head])

        permutation_counts = defaultdict(int)
        for window_tup in rawslider(ouroboros, template_size):
            permutation_counts[window_tup] += 1

        normalised_counts = []
        for count in permutation_counts.values():
            normcount = count / n
            normalised_counts.append(normcount)

        total = sum(normcount * log(normcount) for normcount in normalised_counts)
        totals.append(total)

    approx_entropy = totals[0] - totals[1]
    statistic = 2 * n * (log(2) - approx_entropy)
    p = gammaincc(2 ** (blocksize - 1), statistic / 2)

    return TestResult(statistic, p)
