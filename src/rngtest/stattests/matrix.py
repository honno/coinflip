from dataclasses import dataclass
from math import exp

import numpy as np
from numpy.linalg import matrix_rank

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks

__all__ = ["binary_matrix_rank"]


@binary_stattest
def binary_matrix_rank(series, nrows=32, ncols=32):  # TODO allow for candidate kwarg
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
