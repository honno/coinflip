from math import floor
from math import sqrt

import numpy as np
from scipy.stats import norm

from coinflip._randtests.result import TestResult
from coinflip._randtests.testutils import check_recommendations
from coinflip._randtests.testutils import randtest

__all__ = ["cusum"]


@randtest()
def cusum(series, heads, tails, reverse=False):
    n = len(series)

    check_recommendations({"n ≥ 100": n >= 100})

    oscillations = series.map({heads: 1, tails: -1})

    if reverse:
        oscillations = oscillations[::1]

    cumulative_sums = oscillations.cumsum()
    abs_cumulative_sums = cumulative_sums.abs()

    max_cusum = abs_cumulative_sums.nlargest(1).iloc[0]

    # TODO this all can be done more elegantly
    start1 = floor((-n / max_cusum + 1) / 4)
    start2 = floor((-n / max_cusum - 3) / 4)
    stop = floor((n / max_cusum - 1) / 4) + 1
    p = (
        1
        - sum(
            norm.cdf((4 * k + 1) * max_cusum / sqrt(n))
            - norm.cdf((4 * k - 1) * max_cusum / sqrt(n))
            for k in np.arange(start1, stop, 1)
        )
        + sum(
            norm.cdf((4 * k + 3) * max_cusum / sqrt(n))
            - norm.cdf((4 * k + 1) * max_cusum / sqrt(n))
            for k in np.arange(start2, stop, 1)
        )
    )

    return CusumTestResult(heads, tails, max_cusum, p)


class CusumTestResult(TestResult):
    def __rich_console__(self, console, options):
        yield self._results_text("max cusum")
