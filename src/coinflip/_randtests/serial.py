from collections import defaultdict
from dataclasses import dataclass
from math import floor
from math import log2
from typing import DefaultDict
from typing import Dict
from typing import Tuple

import pandas as pd
from rich.table import Table
from rich.text import Text
from scipy.special import gammaincc

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import MultiTestResult
from coinflip._randtests.common.result import SubTestResult
from coinflip._randtests.common.testutils import slider
from coinflip._randtests.common.typing import Face
from coinflip._randtests.common.typing import Float
from coinflip._randtests.common.typing import Integer

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
    blocksize: Integer
    permutation_counts: Dict[Integer, DefaultDict[Tuple[Face, ...], Integer]]
    normalised_sums: Dict[Integer, Float]

    def _render(self):
        first, second = list(self.results.items())

        f_first = first[1]._pretty_result(prefix="first", stat_varname="delta psi²")
        f_second = second[1]._pretty_result(prefix="second", stat_varname="delta² psi²")

        yield f_first
        yield f_second

        yield self._pretty_inputs(("blocksize", self.blocksize),)

    @classmethod
    def _render_single(
        cls, feature: str, feature_notation: str, result: SubTestResult
    ) -> Table:
        grid = Table.grid(padding=(1))

        title = Text(feature, style="bold")
        grid.add_row(title)

        grid.add_row(f_result)

        return grid
