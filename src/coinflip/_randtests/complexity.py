from copy import copy
from dataclasses import dataclass
from math import floor
from math import sqrt
from typing import List

from scipy.stats import chisquare

from coinflip._randtests.common.collections import Bins
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_chisquare_table
from coinflip._randtests.common.testutils import check_recommendations
from coinflip._randtests.common.testutils import randtest
from coinflip._randtests.common.testutils import rawblocks

__all__ = ["linear_complexity"]


# TODO - remove hardcoded degrees of freedom
#      - dynamically calculate these probabilities
df = 6
probabilities = [
    0.010417,
    0.03125,
    0.125,
    0.5,
    0.25,
    0.0625,
    0.020833,
]


@randtest()
def linear_complexity(series, heads, tails, blocksize=None):
    n = len(series)

    if not blocksize:
        for blocksize in [1000, 2500, 500, 5000]:
            nblocks = n // blocksize
            if 500 <= blocksize <= 5000 and nblocks >= 200:
                break
        else:
            blocksize = max(floor(sqrt(n)), 2)

    nblocks = n // blocksize
    check_recommendations(
        {
            "n ≥ 1000000": n >= 1000000,
            "500 ≤ blocksize ≤ 5000": 500 <= blocksize <= 5000,
            "nblocks ≥ 200": nblocks >= 200,
        }
    )

    binary = series.map({heads: 1, tails: 0})

    expected_mean = (
        blocksize / 2
        + (9 + (-(1 ** (blocksize + 1)))) / 36
        - (blocksize / 3 + 2 / 9) / 2 ** blocksize
    )
    expected_bincounts = [nblocks * prob for prob in probabilities]

    variance_bins = Bins([-3, -2, -1, 0, 1, 2, 3])
    for block_tup in rawblocks(binary, blocksize):
        linear_complexity = berlekamp_massey(block_tup)
        variance = (-1) ** blocksize * (linear_complexity - expected_mean) + 2 / 9
        variance_bins[variance] += 1

    statistic, p = chisquare(list(variance_bins.values()), expected_bincounts)

    return LinearComplexityTestResult(
        heads, tails, statistic, p, blocksize, expected_bincounts, variance_bins
    )


@dataclass
class LinearComplexityTestResult(TestResult):
    blocksize: int
    expected_bincounts: List[float]
    variance_bins: Bins

    def _render(self):
        yield self._pretty_result("chi-square")

        table = make_chisquare_table(
            "variance",
            self.variance_bins.keys(),
            self.expected_bincounts,
            self.variance_bins.values(),
        )
        yield table


def berlekamp_massey(sequence: List[int]) -> int:
    n = len(sequence)

    error_locator = [0 for _ in range(n)]
    error_locator[0] = 1

    error_locator_prev = copy(error_locator)

    min_size = 0  # of the LSFR
    nloops = -1  # since error_locator_prev and min_size were updated

    for i, seq_bit in enumerate(sequence):
        discrepancy = seq_bit
        seq_window = reversed(sequence[i - min_size : i])
        errloc_window = error_locator[1 : min_size + 1]
        for seq_bit, errloc_bit in zip(seq_window, errloc_window):
            product = seq_bit & errloc_bit
            discrepancy = discrepancy ^ product

        if discrepancy:
            error_locator_temp = copy(error_locator)

            recalc_bits = []
            for errloc_bit, prev_bit in zip(
                error_locator[i - nloops : n], error_locator_prev
            ):
                bit = errloc_bit ^ prev_bit
                recalc_bits.append(bit)
            error_locator[i - nloops : n] = recalc_bits

            if min_size <= i / 2:
                min_size = i + 1 - min_size
                nloops = i
                error_locator_prev = error_locator_temp

    return min_size