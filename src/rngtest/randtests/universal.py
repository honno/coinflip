from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from math import erfc
from math import floor
from math import isclose
from math import log
from math import sqrt
from typing import NamedTuple

from rngtest.randtests._collections import FloorDict
from rngtest.randtests._decorators import randtest
from rngtest.randtests._exceptions import TestNotImplementedError
from rngtest.randtests._result import TestResult
from rngtest.randtests._testutils import check_recommendations
from rngtest.randtests._testutils import rawblocks

__all__ = ["maurers_universal"]


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


class DefaultParams(NamedTuple):
    blocksize: int
    init_nblocks: int


# Values taken from "A Statistical Test Suite for Random and Pseudorandom Number
#                    Generators for Cryptographic Applications"
#     See section 2.9.7, "Input Size Recommendation", p. 45
n_defaults = FloorDict(
    {
        387840: DefaultParams(6, 640),
        904960: DefaultParams(7, 1280),
        2068480: DefaultParams(8, 2560),
        4654080: DefaultParams(9, 5120),
        10342400: DefaultParams(10, 10240),
        22753280: DefaultParams(11, 20480),
        49643520: DefaultParams(12, 40960),
        107560960: DefaultParams(13, 81920),
        231669760: DefaultParams(14, 163840),
        496435200: DefaultParams(15, 327680),
        1059061760: DefaultParams(16, 655360),
    }
)


@randtest(min_input=4, rec_input=387840)
def maurers_universal(series, blocksize=None, init_nblocks=None):
    """Distance between patterns is compared to expected result

    Unique permutations in an initial sequence are identified, and the
    distances of aforementioned permutations in a remaining sequence are
    accumulated. The normalised value for the accumulated distances is then
    compared to a hypothetically truly random RNG.


    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    blocksize : `int`
        Size of the blocks that form a permutation
    init_nblocks : `int`
        Number of initial blocks to identify permutations

    Returns
    -------
    TestResult
        Dataclass that contains the test's statistic and p-value
    """
    if blocksize and blocksize > 16:
        # TODO review this policy
        raise TestNotImplementedError(
            "Test implementation cannot handle blocksize over 16"
        )

    n = len(series)

    if not blocksize or not init_nblocks:
        try:
            blocksize, init_nblocks = n_defaults[n]
        except KeyError:
            blocksize = min(max(ceil(log(n)), 2), 16)  # largest blocksize_dists key
            nblocks = n // blocksize
            init_nblocks = max(nblocks // 100, 1)

    init_n = init_nblocks * blocksize
    init_series, spare_series = series[:init_n], series[init_n:]
    spare_nblocks = (n - init_n) / blocksize

    check_recommendations(
        {
            "6 ≤ blocksize ≤ 16": 6 <= blocksize <= 16,
            "init_nblocks ≈ 10 * 2 ** spare_nblocks": isclose(
                init_nblocks, 10 * 2 ** spare_nblocks
            ),
            "spare_nblocks ≈ ⌈n / blocksize⌉ - init_nblocks": isclose(
                spare_nblocks, floor(n / blocksize) - init_nblocks
            ),
        }
    )

    last_occurences = defaultdict(int)

    init_blocks = rawblocks(init_series, blocksize=blocksize)
    for pos, permutation in enumerate(init_blocks, 1):
        last_occurences[permutation] = pos

    spare_blocks = rawblocks(spare_series, blocksize=blocksize)
    spare_firstpos = init_nblocks + 1
    distances_total = 0
    for pos, permutation in enumerate(spare_blocks, spare_firstpos):
        last_occurence = last_occurences[permutation]
        distance = pos - last_occurence
        distances_total += log(distance, 2)

        last_occurences[permutation] = pos

    statistic = distances_total / spare_nblocks
    expected_mean, variance = blocksize_dists[blocksize]
    p = erfc(abs((statistic - expected_mean) / (sqrt(2 * variance))))

    return UniversalTestResult(statistic=statistic, p=p)


@dataclass
class UniversalTestResult(TestResult):
    def __str__(self):
        return self.stats_table("normalised distances")
