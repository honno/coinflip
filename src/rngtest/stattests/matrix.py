from dataclasses import dataclass
from math import exp

import numpy as np
from numpy.linalg import matrix_rank

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks

__all__ = ["binary_matrix_rank"]


# TODO use candidate kwarg to convert sequences into {0, 1} sequences
@binary_stattest
def binary_matrix_rank(series, nrows=32, ncols=32):
    """Independence of neighbouring sequences is compared to expected result

    Independence is determined by the matrix rank of a subsequence, where it is
    split into multiple rows to form a matrix. The counts of different rank bins
    is referenced to a hypothetically truly random RNG.

    Parameters
    ----------
    series : Series
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

    matrices = []
    for chunk in chunks(series, blocksize=blocksize):
        rows = [row.values for row in chunks(chunk, nblocks=nrows)]
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
