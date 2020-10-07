from math import floor
from math import sqrt

import numpy as np
from scipy.stats import norm

from coinflip.randtests._decorators import elected
from coinflip.randtests._decorators import randtest
from coinflip.randtests._result import TestResult
from coinflip.randtests._testutils import check_recommendations

__all__ = ["cusum"]


@randtest()
@elected
def cusum(series, candidate, reverse=False):
    n = len(series)

    check_recommendations({"n ≥ 100": n >= 100})

    peak = candidate
    trough = next(value for value in series.unique() if value != candidate)

    oscillations = series.map({peak: 1, trough: -1})

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

    return TestResult(max_cusum, p)
