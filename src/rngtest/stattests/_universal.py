from collections import defaultdict
from math import erfc
from math import log
from math import sqrt
from typing import NamedTuple

from rngtest.stattests._common import TestResult
from rngtest.stattests._common import rawchunks
from rngtest.stattests._common import stattest

__all__ = ["maurers_universal"]


# TODO understand what's going with the hard coded values provided
@stattest
def maurers_universal(series, blocksize, init_nblocks):
    n = len(series)
    init_n = init_nblocks * blocksize
    init_series, spare_series = series[:init_n], series[init_n:]
    spare_nblocks = (n - init_n) / blocksize

    last_occurences = defaultdict(int)

    init_blocks = rawchunks(init_series, blocksize=blocksize)
    for pos, permutation in enumerate(init_blocks, 1):
        last_occurences[permutation] = pos

    spare_blocks = rawchunks(spare_series, blocksize=blocksize)
    spare_firstpos = init_nblocks + 1
    distances_total = 0
    for pos, permutation in enumerate(spare_blocks, spare_firstpos):
        last_occurence = last_occurences[permutation]
        distance = pos - last_occurence
        distances_total += log(distance, 2)

        last_occurences[permutation] = pos

    statistic = distances_total / spare_nblocks
    expected_mean, variance = blocksize_dists[blocksize]
    p = erfc(abs((statistic - expected_mean) / (sqrt(2) * variance)))

    return TestResult(statistic=statistic, p=p)


class Dist(NamedTuple):
    mean: float
    variance: float


# Values taken from "A Handbook of Applied Cryptography"
#     See section 5.4.5, "Maurer's universal statistical test", p. 184
# TODO generate this dynamically
blocksize_dists = {
    1: Dist(0.7326495, 0.690),
    2: Dist(1.5374383, 1.338),
    3: Dist(2.4016068, 1.901),
    4: Dist(3.3112247, 2.358),
    5: Dist(4.2534266, 2.705),
    6: Dist(5.2177052, 2.954),
    7: Dist(6.1962507, 3.125),
    8: Dist(7.1836656, 3.238),
    9: Dist(8.1764248, 3.311),
    10: Dist(9.1723243, 3.356),
    11: Dist(10.170032, 3.384),
    12: Dist(11.168765, 3.401),
    13: Dist(12.168070, 3.410),
    14: Dist(13.167693, 3.416),
    15: Dist(14.167488, 3.419),
    16: Dist(15.167379, 3.421),
}

# TODO default parameters using NIST's recommendations
# n blocksize init_nblocks
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
