from dataclasses import astuple
from dataclasses import dataclass
from math import exp
from math import floor
from math import sqrt
from typing import Iterable
from typing import Tuple

from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_testvars_table
from coinflip._randtests.common.result import vars_list
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.testutils import check_recommendations
from coinflip._randtests.common.testutils import randtest
from coinflip._randtests.common.testutils import rawblocks

__all__ = ["binary_matrix_rank", "matrix_rank"]


@dataclass
class RankCounts:
    full: int = 0
    runnerup: int = 0
    remaining: int = 0


@randtest(min_n=4)
def binary_matrix_rank(series, heads, tails, matrix_dimen: Tuple[int, int] = None):
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

    check_recommendations(
        {
            "n ≥ 128": n >= 152,  # nblocks=38, blocksize=4
            "n ≥ 38 * blocksize": n >= 38 * blocksize,
        }
    )

    fullrank = min(nrows, ncols)

    # TODO find expressive and performative calculation for constants
    expected_rankcounts = RankCounts(
        full=0.2888 * nblocks, runnerup=0.5776 * nblocks, remaining=0.1336 * nblocks,
    )

    rankable_series = series.map({heads: 1, tails: 0})

    matrices = []
    for block in blocks(rankable_series, blocksize):
        matrix = [row for row in rawblocks(block, nblocks=nrows)]
        matrices.append(matrix)

    ranks = [matrix_rank(matrix) for matrix in matrices]

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
        heads,
        tails,
        statistic,
        p,
        nrows,
        ncols,
        fullrank,
        expected_rankcounts,
        rankcounts,
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

    def __rich_console__(self, console, options):
        yield self._results_text("chi-square")

        yield ""

        yield vars_list(
            ("nrows", self.nrows), ("ncols", self.ncols),
        )

        runnerup = self.fullrank - 1
        remaining = runnerup - 1
        f_ranks = [
            str(self.fullrank),
            str(runnerup),
            "0" if remaining == 0 else f"0-{remaining}",
        ]

        table = zip(
            f_ranks,
            astuple(self.rankcounts),
            astuple(self.expected_rankcounts),
            self.rankcount_diffs,
        )
        f_table = make_testvars_table("rank", "count", "expected", "diff")
        for f_rank, count, count_expect, diff in table:
            f_count = str(count)
            f_count_expect = str(round(count_expect, 1))
            f_diff = str(round(diff, 1))
            f_table.add_row(f_rank, f_count, f_count_expect, f_diff)

        yield f_table


def matrix_rank(matrix: Iterable[Iterable[int]]) -> int:
    """Finds the rank of a binary matrix

    Parameters
    ----------
    matrix : ``Iterable[Iterable[int]]``
        Binary matrix to rank

    Returns
    -------
    rank : int
        Rank of ``matrix``

    Notes
    -----
    Implementaton inpisred by a `StackOverflow answer
    <https://stackoverflow.com/a/56858995/5193926>`_ from Mark Dickinson.
    """
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


def bits2int(bits: Iterable[int]) -> int:
    """Converts a list of bits into a numerical representation"""
    num = 0
    for bit in bits:
        num = (num << 1) | bit

    return num
