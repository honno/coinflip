from dataclasses import dataclass
from math import exp

import numpy as np
from numpy.linalg import matrix_rank

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks

__all__ = ["binary_matrix_rank"]


# TODO allow for candidate kwarg
@binary_stattest
def binary_matrix_rank(series, matrix_rows=32, matrix_cols=32):
    n = len(series)
    block_size = matrix_rows * matrix_cols
    nblocks = n // block_size

    matrices = []
    for chunk in chunks(series, block_size=block_size):
        rows_as_series = chunks(chunk, nblocks=matrix_rows)
        rows_as_arrays = [series.values for series in rows_as_series]
        matrix = np.stack(rows_as_arrays)
        matrices.append(matrix)

    ranks = [matrix_rank(matrix) for matrix in matrices]

    counts = RankCounts()
    for rank in ranks:
        if rank == matrix_rows:
            counts.full_rank += 1
        elif rank == matrix_rows - 1:
            counts.runner_up_rank += 1
        else:
            counts.remaining_ranks += 1

    statistic = sum(
        [
            (counts.full_rank - (0.2888 * nblocks)) ** 2 / (0.2888 * nblocks),
            (counts.runner_up_rank - (0.5776 * nblocks)) ** 2 / (0.5776 * nblocks),
            (counts.remaining_ranks - (0.1336 * nblocks)) ** 2 / (0.1336 * nblocks),
        ]
    )
    p = exp(-statistic / 2)

    return TestResult(statistic=statistic, p=p)


@dataclass
class RankCounts:
    full_rank: int = 0
    runner_up_rank: int = 0
    remaining_ranks: int = 0
