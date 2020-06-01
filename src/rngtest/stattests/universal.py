from collections import defaultdict
from math import erfc
from math import log
from math import sqrt
from typing import Any
from typing import Iterable
from typing import Tuple

import pandas as pd

from rngtest.stattests.common.decorators import binary_stattest
from rngtest.stattests.common.methods import chunks
from rngtest.stattests.common.result import TestResult

__all__ = ["maurers_universal"]


# TODO understand what's going with the hard coded values provided
@binary_stattest
def maurers_universal(series, block_size, init_nblocks):
    n = len(series)
    init_n = init_nblocks * block_size
    init_series, remaining_series = series[:init_n], series[init_n:]
    remaining_nblocks = (n - init_n) / block_size

    last_permutation_occurences = defaultdict(int)

    init_blocks = hashable_chunks(init_series, block_size=block_size)
    for i, permutation in enumerate(init_blocks, 1):
        last_permutation_occurences[permutation] = i

    remaining_blocks = hashable_chunks(remaining_series, block_size=block_size)
    cumulative_distances = 0
    for i, permutation in enumerate(remaining_blocks, init_nblocks + 1):
        last_occurence = last_permutation_occurences[permutation]
        distance = i - last_occurence
        cumulative_distances += log(distance, 2)

        last_permutation_occurences[permutation] = i

    statistic = cumulative_distances / remaining_nblocks

    stuff = hard_coded_thing.loc[hard_coded_thing["block_size"] == block_size]

    p = erfc(abs((statistic - stuff["expected_value"]) / (sqrt(2) * stuff["variance"])))

    return TestResult(statistic=statistic, p=p)


# TODO generate this dynamically
hard_coded_thing = pd.DataFrame(
    [
        [2, 1.5374383, 1.338],
        [6, 5.2177052, 2.954],
        [7, 6.1962507, 3.125],
        [8, 7.1836656, 3.238],
        [9, 8.1764248, 3.311],
        [10, 9.1723243, 3.356],
        [11, 10.170032, 3.384],
        [12, 11.168765, 3.401],
        [13, 12.168070, 3.410],
        [14, 13.167693, 3.416],
        [15, 14.167488, 3.419],
        [16, 15.167379, 3.421],
    ],
    columns=["block_size", "expected_value", "variance"],
)


def hashable_chunks(*args, **kwargs) -> Iterable[Tuple[Any]]:
    for chunk in chunks(*args, **kwargs):
        yield tuple(chunk.tolist())


# TODO default parameters using NIST's recommendations
# n block_size init_nblocks
# 387,840 6 640
# 904,960 7 1280
# 2,068,480 8 2560
# 4,654,080 9 5120
# 10,342,400 10 10240
# 22,753,280 11 20480
# 49,643,520 12 40960
# 107,560,960 13 81920
# 231,669,760 14 163840
# 496,435,200 15 327680
# 1,059,061,760 16 655360
