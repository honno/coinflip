from collections import defaultdict
from dataclasses import dataclass
from math import floor
from math import log2
from typing import DefaultDict
from typing import Dict
from typing import Tuple

import pandas as pd
from nptyping import Float
from nptyping import Int
from rich import box
from rich.table import Table
from scipy.special import gammaincc

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import Face
from coinflip._randtests.common.result import MultiTestResult
from coinflip._randtests.common.result import SubTestResult
from coinflip._randtests.common.testutils import slider

__all__ = ["serial"]


@randtest()
def serial(series, heads, tails, ctx, blocksize=None):
    n = len(series)

    if not blocksize:
        blocksize = max(floor(log2(n)) - 2 - 1, 2)

    set_task_total(ctx, (1 + n) * 3 + 2)

    failures = check_recommendations(
        ctx, {"blocksize < ⌊log2(n) - 2⌋": blocksize < floor(log2(n)) - 2}
    )

    permutation_counts = {}
    normalised_sums = {}
    for window_size in [blocksize, blocksize - 1, blocksize - 2]:
        if window_size > 0:
            head = series[: window_size - 1]
            ouroboros = pd.concat([series, head])

            advance_task(ctx)

            counts = defaultdict(int)
            for window_tup in slider(ouroboros, window_size):
                counts[window_tup] += 1

                advance_task(ctx)

            permutation_counts[window_size] = counts

            sum_squares = sum(count ** 2 for count in counts.values())
            normsum = (2 ** window_size / n) * sum_squares - n

            normalised_sums[window_size] = normsum

        else:
            permutation_counts[window_size] = defaultdict(int)
            normalised_sums[window_size] = 0

    advance_task(ctx)

    normsum_delta1 = normalised_sums[blocksize] - normalised_sums[blocksize - 1]
    p1 = gammaincc(2 ** (blocksize - 2), normsum_delta1 / 2)

    normsum_delta2 = (
        normalised_sums[blocksize]
        - 2 * normalised_sums[blocksize - 1]
        + normalised_sums[blocksize - 2]
    )
    p2 = gammaincc(2 ** (blocksize - 3), normsum_delta2 / 2)

    advance_task(ctx)

    results = {
        "∇ψ²ₘ": SubTestResult(normsum_delta1, p1,),
        "∇²ψ²ₘ": SubTestResult(normsum_delta2, p2,),
    }

    return SerialMultiTestResult(
        heads, tails, failures, results, blocksize, permutation_counts, normalised_sums,
    )


@dataclass
class SerialMultiTestResult(MultiTestResult):
    blocksize: Int
    permutation_counts: Dict[Int, DefaultDict[Tuple[Face, ...], Int]]
    normalised_sums: Dict[Int, Float]

    def _render(self):
        yield self._pretty_inputs(("blocksize", self.blocksize),)

        grid = Table(*self.results.keys(), box=box.MINIMAL)

        result1, result2 = self.results.values()
        f_result1 = result1._pretty_result("delta psi²")
        f_result2 = result2._pretty_result("delta² psi²")
        grid.add_row(f_result1, f_result2)

        yield grid

    def _render_sub(self, result: SubTestResult):
        yield result
