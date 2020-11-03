from collections import defaultdict
from dataclasses import dataclass
from math import floor
from math import log
from math import log2

import pandas as pd
from scipy.special import gammaincc

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.testutils import slider
from coinflip._randtests.common.typing import Integer

__all__ = ["approximate_entropy"]


@randtest()
def approximate_entropy(series, heads, tails, ctx, blocksize=None):
    n = len(series)

    if not blocksize:
        blocksize = max(floor(log2(n)) - 5 - 1, 2)

    set_task_total(ctx, (n + 2) * 2 + 1)

    failures = check_recommendations(
        ctx, {"blocksize < ⌊log2(n)⌋ - 5": blocksize < floor(log2(n)) - 5}
    )

    phis = []
    for template_size in [blocksize, blocksize + 1]:
        head = series[: template_size - 1]
        ouroboros = pd.concat([series, head])

        permutation_counts = defaultdict(int)
        for window_tup in slider(ouroboros, template_size):
            permutation_counts[window_tup] += 1

            advance_task(ctx)

        normalised_counts = []
        for count in permutation_counts.values():
            normcount = count / n
            normalised_counts.append(normcount)

        advance_task(ctx)

        phi = sum(normcount * log(normcount) for normcount in normalised_counts)
        phis.append(phi)

        advance_task(ctx)

    approx_entropy = phis[0] - phis[1]
    chi2 = 2 * n * (log(2) - approx_entropy)
    p = gammaincc(2 ** (blocksize - 1), chi2 / 2)

    advance_task(ctx)

    return ApproximateEntropyTestResult(heads, tails, failures, chi2, p, blocksize)


@dataclass
class ApproximateEntropyTestResult(TestResult):
    blocksize: Integer

    def _render(self):
        yield self._pretty_result("chi-square")
