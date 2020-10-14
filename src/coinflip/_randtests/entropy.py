from collections import defaultdict
from dataclasses import dataclass
from math import floor
from math import log
from math import log2

import pandas as pd
from scipy.special import gammaincc

from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.testutils import check_recommendations
from coinflip._randtests.common.testutils import randtest
from coinflip._randtests.common.testutils import slider

__all__ = ["approximate_entropy"]


@randtest()
def approximate_entropy(series, heads, tails, blocksize=None):
    n = len(series)

    if not blocksize:
        blocksize = max(floor(log2(n)) - 5 - 1, 2)

    check_recommendations({"blocksize < ⌊log2(n)⌋ - 5": blocksize < floor(log2(n)) - 5})

    totals = []
    for template_size in [blocksize, blocksize + 1]:
        head = series[: template_size - 1]
        ouroboros = pd.concat([series, head])

        permutation_counts = defaultdict(int)
        for window_tup in slider(ouroboros, template_size, overlap=True):
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

    return ApproximateEntropyTestResult(heads, tails, statistic, p, blocksize)


@dataclass
class ApproximateEntropyTestResult(TestResult):
    blocksize: int

    def _render(self):
        yield self._pretty_result("chi-square")
