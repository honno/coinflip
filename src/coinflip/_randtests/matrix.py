from dataclasses import astuple
from dataclasses import dataclass
from math import floor
from math import sqrt
from typing import Iterable
from typing import Tuple

from scipy.stats import chisquare
from typing_extensions import Literal

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_chisquare_table
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.testutils import rawblocks
from coinflip._randtests.common.typing import Integer

__all__ = ["binary_matrix_rank", "matrix_rank"]


@dataclass
class RankCounts:
    full: Integer = 0
    runnerup: Integer = 0
    remaining: Integer = 0


@randtest(min_n=4)
def binary_matrix_rank(
    series, heads, tails, ctx, matrix_dimen: Tuple[Integer, Integer] = None
):
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

    set_task_total(ctx, nblocks + 3)

    failures = check_recommendations(
        ctx,
        {
            "n ≥ 128": n >= 152,  # nblocks=38, blocksize=4
            "n ≥ 38 * blocksize": n >= 38 * blocksize,
        },
    )

    fullrank = min(nrows, ncols)

    # TODO find expressive and performative calculation for constants
    expected_rankcounts = RankCounts(
        full=0.2888 * nblocks, runnerup=0.5776 * nblocks, remaining=0.1336 * nblocks,
    )

    rankable_series = series.map({heads: 1, tails: 0})

    advance_task(ctx)

    ranks = []
    for block in blocks(rankable_series, blocksize):
        matrix = [row for row in rawblocks(block, ncols)]

        rank = matrix_rank(matrix)

        advance_task(ctx)

        ranks.append(rank)

    rankcounts = RankCounts()
    for rank in ranks:
        if rank == fullrank:
            rankcounts.full += 1
        elif rank == fullrank - 1:
            rankcounts.runnerup += 1
        else:
            rankcounts.remaining += 1

    advance_task(ctx)

    statistic, p = chisquare(astuple(rankcounts), astuple(expected_rankcounts))

    advance_task(ctx)

    return BinaryMatrixRankTestResult(
        heads,
        tails,
        failures,
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
    nrows: Integer
    ncols: Integer
    fullrank: Integer
    expected_rankcounts: RankCounts
    rankcounts: RankCounts

    def _render(self):
        yield self._pretty_result("chi-square")

        yield TestResult._pretty_inputs(
            ("nrows", self.nrows), ("ncols", self.ncols),
        )

        runnerup = self.fullrank - 1
        remaining = runnerup - 1
        f_ranks = [
            str(self.fullrank),
            str(runnerup),
            "0" if remaining == 0 else f"0-{remaining}",
        ]

        table = make_chisquare_table(
            "rank of matrix",
            "ranks",
            f_ranks,
            astuple(self.expected_rankcounts),
            astuple(self.rankcounts),
        )

        yield table


def matrix_rank(matrix: Iterable[Iterable[Literal[0, 1]]]) -> Integer:
    """Finds the rank of a binary matrix

    Parameters
    ----------
    matrix : ``Iterable[Iterable[Integer]]``
        Binary matrix to rank

    Returns
    -------
    rank : Integer
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


def bits2int(bits: Iterable[Literal[0, 1]]) -> Integer:
    """Converts a list of bits into a numerical representation"""
    num = 0
    for bit in bits:
        num = (num << 1) | bit

    return num
