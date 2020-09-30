from copy import copy
from typing import List

from scipy.special import gammaincc

from coinflip.randtests._collections import Bins
from coinflip.randtests._decorators import elected
from coinflip.randtests._decorators import randtest
from coinflip.randtests._result import TestResult
from coinflip.randtests._testutils import check_recommendations
from coinflip.randtests._testutils import rawblocks

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


@randtest(rec_input=1000000)
@elected
def linear_complexity(series, candidate, blocksize):
    n = len(series)

    nblocks = n // blocksize
    check_recommendations(
        {
            "500 ≤ blocksize ≤ 5000": 500 <= blocksize <= 5000,
            "nblocks ≥ 200": nblocks >= 200,
        }
    )

    noncandidate = next(value for value in series.unique() if value != candidate)
    binary = series.map({candidate: 1, noncandidate: 0})

    expected_mean = (
        blocksize / 2
        + (9 + (-(1 ** (blocksize + 1)))) / 36
        - (blocksize / 3 + 2 / 9) / 2 ** blocksize
    )
    expected_bincounts = [nblocks * prob for prob in probabilities]

    # TODO more appropiate name for counts and t
    counts = Bins([-2.5, -1.5, -0.5, -0.5, 0.5, 1.5, 2.5])
    for block_tup in rawblocks(binary, blocksize):
        linear_complexity = berlekamp_massey(block_tup)
        t = -(1 ** blocksize) * (linear_complexity - expected_mean) + 2 / 9
        counts[t] += 1

    reality_check = []
    for count_expect, count in zip(expected_bincounts, counts.values()):
        diff = (count - count_expect) ** 2 / count_expect
        reality_check.append(diff)

    statistic = sum(reality_check)
    p = gammaincc(df / 2, statistic / 2)

    return TestResult(statistic, p)


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
