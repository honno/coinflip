from dataclasses import dataclass
from math import floor
from math import sqrt

import numpy as np
from scipy.stats import norm

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.typing import Bool

__all__ = ["cusum"]


@randtest()
def cusum(series, heads, tails, ctx, reverse=False):
    n = len(series)

    set_task_total(ctx, 3)

    failures = check_recommendations(ctx, {"n ≥ 100": n >= 100})

    oscillations = series.map({heads: 1, tails: -1})

    advance_task(ctx)

    if reverse:
        oscillations = oscillations[::-1]

    cusums = oscillations.cumsum()
    abs_cusums = cusums.abs()
    max_cusum = abs_cusums.nlargest(1).iloc[0]

    advance_task(ctx)

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

    advance_task(ctx)

    return CusumTestResult(heads, tails, failures, max_cusum, p, reverse)


@dataclass
class CusumTestResult(TestResult):
    reverse: Bool

    def _render(self):
        yield self._pretty_result("max cusum")
