from dataclasses import astuple
from dataclasses import dataclass
from math import exp
from typing import Tuple

import numpy as np
from numpy.linalg import matrix_rank
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


@stattest(min_input=152)  # nblocks=38, blocksize=4
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
            blocksize = n // 38
            nrows = blocksize // 2
            ncols = nrows
    else:
        nrows, ncols = matrix_dimen

    blocksize = nrows * ncols
    nblocks = n // blocksize

    fullrank = min(nrows, ncols)

    # TODO find expressive and performative calculation for constants
    rankcounts_expect = RankCounts(
        full=0.2888 * nblocks, runnerup=0.5776 * nblocks, remaining=0.1336 * nblocks,
    )

    noncandidate = next(value for value in series.unique() if value != candidate)
    rankable_series = series.map({candidate: 1, noncandidate: 0})

    matrices = []
    for block in blocks(rankable_series, blocksize=blocksize):
        rows = [row for row in rawblocks(block, nblocks=nrows)]
        matrix = np.stack(rows)
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
    for count, count_expect in zip(astuple(rankcounts), astuple(rankcounts_expect)):
        diff = (count - count_expect) ** 2 / count_expect
        reality_check.append(diff)

    statistic = sum(reality_check)
    p = exp(-statistic / 2)

    return BinaryMatrixRankTestResult(
        statistic=statistic,
        p=p,
        fullrank=fullrank,
        rankcounts_expect=rankcounts_expect,
        rankcounts=rankcounts,
    )


@dataclass
class BinaryMatrixRankTestResult(TestResult):
    fullrank: int
    rankcounts_expect: RankCounts
    rankcounts: RankCounts

    def __post_init__(self):
        counts = astuple(self.rankcounts)
        counts_expect = astuple(self.rankcounts_expect)

        self.rankcount_diffs = []
        for expected, actual in zip(counts_expect, counts):
            diff = expected - actual
            self.rankcount_diffs.append(diff)

    def __str__(self):
        runnerup = self.fullrank - 1
        remaining = runnerup - 1
        f_ranks = [
            str(self.fullrank),
            str(runnerup),
            "0" if remaining == 0 else f"0-{remaining}",
        ]

        f_counts = astuple(self.rankcounts)

        counts_expect = astuple(self.rankcounts_expect)
        f_counts_expect = [f"~{round(count, 1)}" for count in counts_expect]

        f_diffs = [round(diff, 1) for diff in self.rankcount_diffs]

        f_table = tabulate(
            zip(f_ranks, f_counts, f_counts_expect, f_diffs),
            headers=["rank", "count", "expected", "diff"],
            colalign=("left", "right", "right", "right"),
        )

        return f"p={self.p3f()}\n" + f_table
