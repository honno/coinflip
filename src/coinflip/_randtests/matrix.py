from dataclasses import astuple
from dataclasses import dataclass
from dataclasses import fields
from math import floor
from math import sqrt
from typing import Iterable
from typing import List
from typing import Tuple

import altair as alt
import pandas as pd
from scipy.stats import chisquare
from typing_extensions import Literal

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_chisquare_table
from coinflip._randtests.common.result import plot_chi2_dist
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.testutils import rawblocks
from coinflip._randtests.common.typing import Integer

__all__ = ["binary_matrix_rank", "matrix_rank"]


@dataclass
class RankCounts:
    remaining: Integer = 0
    runnerup: Integer = 0
    full: Integer = 0


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
        remaining=0.1336 * nblocks,
        runnerup=0.5776 * nblocks,
        full=0.2888 * nblocks,
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

    def _fmt_rank_ranges(self) -> List[str]:
        runnerup = self.fullrank - 1
        remaining = runnerup - 1
        f_ranks = [
            "0" if remaining == 0 else f"0-{remaining}",
            str(runnerup),
            str(self.fullrank),
        ]

        return f_ranks

    def _render(self):
        yield self._pretty_result("chi-square")

        yield TestResult._pretty_inputs(
            ("nrows", self.nrows),
            ("ncols", self.ncols),
        )

        f_ranks = self._fmt_rank_ranges()

        table = make_chisquare_table(
            "rank of matrix",
            "ranks",
            f_ranks,
            astuple(self.expected_rankcounts),
            astuple(self.rankcounts),
        )

        yield table

    def plot_rank_counts(self):
        df = pd.DataFrame(
            {
                "rank_range": self._fmt_rank_ranges(),
                "expected": astuple(self.expected_rankcounts),
                "observed": astuple(self.rankcounts),
            }
        )
        df = df.melt("rank_range", var_name="type", value_name="nblocks")

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                alt.X(
                    "rank_range:O",
                    title="Matrix rank",
                ),
                alt.Y(
                    "nblocks:Q",
                    title="Number of blocks",
                    axis=alt.Axis(tickMinStep=1),
                ),
                column=alt.Column(
                    "type:N",
                    title=None,
                ),
            )
            .properties(title="Matrix rank per block")
        )

        return chart

    def plot_refdist(self):
        return plot_chi2_dist(self.statistic, len(fields(self.rankcounts)))


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
