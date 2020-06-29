from dataclasses import astuple
from dataclasses import dataclass
from math import exp
from math import floor
from math import sqrt
from typing import Tuple

from tabulate import tabulate

from rngtest.stattests._common import TestResult
from rngtest.stattests._common import blocks
from rngtest.stattests._common import elected
from rngtest.stattests._common import rawblocks
from rngtest.stattests._common import stattest

__all__ = ["binary_matrix_rank"]


@dataclass
class RankCounts:
    full: int = 0
    runnerup: int = 0
    remaining: int = 0


# TODO counts are wrong
@stattest(min_input=4, rec_input=152)  # nblocks=38, blocksize=4
@elected
def binary_matrix_rank(series, candidate, matrix_dimen: Tuple[int, int] = None):
    """Independence of neighbouring sequences is compared to expected result

    Independence is determined by the matrix rank of a subsequence, where it is
    split into multiple rows to form a matrix. The counts of different rank bins
    is referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    matrix_dimen : `Tuple[int, int]`
        Number of rows and columns in each matrix

    Returns
    -------
    BinaryMatrixRankTestResult
        Dataclass that contains the test's statistic and p-value
    """
    n = len(series)

    if matrix_dimen is None:
        if n // (32 * 32) > 38:
            nrows = 32
            ncols = 32
        else:
            blocksize = max(n // 38, 4)
            nrows = floor(sqrt(blocksize))
            ncols = nrows
    else:
        nrows, ncols = matrix_dimen

    blocksize = nrows * ncols
    nblocks = n // blocksize

    fullrank = min(nrows, ncols)

    # TODO find expressive and performative calculation for constants
    expected_rankcounts = RankCounts(
        full=0.2888 * nblocks, runnerup=0.5776 * nblocks, remaining=0.1336 * nblocks,
    )

    noncandidate = next(value for value in series.unique() if value != candidate)
    rankable_series = series.map({candidate: 1, noncandidate: 0})

    matrices = []
    for block in blocks(rankable_series, blocksize=blocksize):
        matrix = [row for row in rawblocks(block, nblocks=nrows)]
        matrices.append(matrix)

    ranks = [gf2_rank(matrix) for matrix in matrices]

    rankcounts = RankCounts()
    for rank in ranks:
        if rank == fullrank:
            rankcounts.full += 1
        elif rank == fullrank - 1:
            rankcounts.runnerup += 1
        else:
            rankcounts.remaining += 1

    reality_check = []
    for count_expect, count in zip(astuple(expected_rankcounts), astuple(rankcounts)):
        diff = (count - count_expect) ** 2 / count_expect
        reality_check.append(diff)

    statistic = sum(reality_check)
    p = exp(-statistic / 2)

    return BinaryMatrixRankTestResult(
        statistic=statistic,
        p=p,
        nrows=nrows,
        ncols=ncols,
        fullrank=fullrank,
        expected_rankcounts=expected_rankcounts,
        rankcounts=rankcounts,
    )


@dataclass
class BinaryMatrixRankTestResult(TestResult):
    nrows: int
    ncols: int
    fullrank: int
    expected_rankcounts: RankCounts
    rankcounts: RankCounts

    def __post_init__(self):
        expected_counts = astuple(self.expected_rankcounts)
        counts = astuple(self.rankcounts)

        self.rankcount_diffs = []
        for expect, actual in zip(expected_counts, counts):
            diff = actual - expect
            self.rankcount_diffs.append(diff)

    def __str__(self):
        f_stats = self.stats_table("chi-square")

        f_matrix_dimen = f"nrows: {self.nrows}\n" f"ncols: {self.ncols}"

        runnerup = self.fullrank - 1
        remaining = runnerup - 1
        f_ranks = [
            str(self.fullrank),
            str(runnerup),
            "0" if remaining == 0 else f"0-{remaining}",
        ]

        f_counts = astuple(self.rankcounts)

        counts_expect = astuple(self.expected_rankcounts)
        f_counts_expect = [round(count, 1) for count in counts_expect]

        f_diffs = [round(diff, 1) for diff in self.rankcount_diffs]

        f_table = tabulate(
            zip(f_ranks, f_counts, f_counts_expect, f_diffs),
            headers=["rank", "count", "expected", "diff"],
        )

        return f"{f_stats}\n" "\n" f"{f_matrix_dimen}\n" "\n" f"{f_table}"


def bits2int(bits):
    num = 0
    for bit in bits:
        num = (num << 1) | bit

    return num


def gf2_rank(matrix):
    numbers = [bits2int(bits) for bits in matrix]

    rank = 0
    while len(numbers) > 0:
        pivot = numbers.pop()
        if pivot:
            rank += 1
            lsb = pivot & -pivot
            for i, num in enumerate(numbers):
                if lsb & num:
                    numbers[i] = num ^ pivot

    return rank
