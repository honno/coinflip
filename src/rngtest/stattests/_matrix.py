from dataclasses import dataclass
from math import exp

import numpy as np
from numpy.linalg import matrix_rank

from rngtest.stattests._common import TestResult
from rngtest.stattests._common import blocks
from rngtest.stattests._common import elected
from rngtest.stattests._common import rawblocks
from rngtest.stattests._common import stattest

__all__ = ["binary_matrix_rank"]


@stattest
@elected
def binary_matrix_rank(series, candidate, nrows=32, ncols=32):
    """Independence of neighbouring sequences is compared to expected result

    Independence is determined by the matrix rank of a subsequence, where it is
    split into multiple rows to form a matrix. The counts of different rank bins
    is referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    nrows : int
        Number of rows in each matrix
    ncols : int
        Number of columns in each matrix

    Returns
    -------
    TestResult
        Dataclass that contains the test's statistic and p-value
    """
    n = len(series)
    blocksize = nrows * ncols
    nblocks = n // blocksize

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
        if rank == nrows:
            rankcounts.full += 1
        elif rank == nrows - 1:
            rankcounts.runnerup += 1
        else:
            rankcounts.remaining += 1

    partials = [
        (rankcounts.full - (0.2888 * nblocks)) ** 2 / (0.2888 * nblocks),
        (rankcounts.runnerup - (0.5776 * nblocks)) ** 2 / (0.5776 * nblocks),
        (rankcounts.remaining - (0.1336 * nblocks)) ** 2 / (0.1336 * nblocks),
    ]
    statistic = sum(partials)
    p = exp(-statistic / 2)

    return TestResult(statistic=statistic, p=p)


@dataclass
class RankCounts:
    full: int = 0
    runnerup: int = 0
    remaining: int = 0
