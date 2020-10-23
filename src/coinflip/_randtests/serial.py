from collections import defaultdict
from dataclasses import dataclass
from math import floor
from math import log2
from typing import DefaultDict
from typing import Dict
from typing import Tuple

import pandas as pd
from rich import box
from rich.table import Table
from scipy.special import gammaincc

from coinflip import encoders as enc
from coinflip._randtests.common.core import *
from coinflip._randtests.common.pprint import pretty_subseq
from coinflip._randtests.common.result import MultiTestResult
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import encode
from coinflip._randtests.common.testutils import slider
from coinflip.typing import Face

__all__ = ["serial"]


@randtest()
def serial(series, heads, tails, ctx, blocksize=None):
    n = len(series)

    if not blocksize:
        blocksize = max(floor(log2(n)) - 2 - 1, 2)

    set_task_total(ctx, (1 + n) * 3 + 2)

    check_recommendations({"blocksize < ⌊log2(n) - 2⌋": blocksize < floor(log2(n)) - 2})

    permutation_counts = {}
    for window_size in [blocksize, blocksize - 1, blocksize - 2]:
        head = series[: window_size - 1]
        ouroboros = pd.concat([series, head])

        advance_task(ctx)

        counts = defaultdict(int)
        for window_tup in slider(ouroboros, window_size):
            counts[window_tup] += 1

            advance_task(ctx)

        permutation_counts[window_size] = counts

    normalised_sums = {}
    for window_size, counts in permutation_counts.items():
        sum_squares = sum(count ** 2 for count in counts.values())
        normsum = (2 ** window_size / n) * sum_squares - n

        normalised_sums[window_size] = normsum

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
        "∇ψ²ₘ": FirstSerialTestResult(
            heads,
            tails,
            normsum_delta1,
            p1,
            blocksize,
            permutation_counts,
            normalised_sums,
        ),
        "∇²ψ²ₘ": SecondSerialTestResult(
            heads,
            tails,
            normsum_delta2,
            p2,
            blocksize,
            permutation_counts,
            normalised_sums,
        ),
    }

    return MultiSerialTestResult(results)


@dataclass
class BaseSerialTestResult(TestResult):
    blocksize: int = encode(enc.int_)
    permutation_counts: Dict[int, DefaultDict[Tuple[Face, ...], int]] = encode(
        enc.dict_(enc.int_, enc.dict_(enc.tuple_(enc.faces), enc.int_))
    )
    normalised_sums: Dict[int, float] = encode(enc.dict_(enc.int_, enc.float_))

    def _pretty_permutation(self, permutation: Tuple):
        return pretty_subseq(permutation, self.heads, self.tails)


@dataclass
class FirstSerialTestResult(BaseSerialTestResult):
    def _render(self):
        yield self._pretty_result("delta psi²")

        yield TestResult._pretty_inputs(("blocksize", self.blocksize))


@dataclass
class SecondSerialTestResult(BaseSerialTestResult):
    def _render(self):
        yield self._pretty_result("delta² psi²")

        yield TestResult._pretty_inputs(("blocksize", self.blocksize))


class MultiSerialTestResult(MultiTestResult):
    def _render(self):
        grid = Table("∇ψ²ₘ test", "∇²ψ²ₘ test", box=box.MINIMAL)

        grid.add_row(*self.values())

        yield grid
