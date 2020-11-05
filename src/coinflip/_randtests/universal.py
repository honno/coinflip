from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from math import erfc
from math import floor
from math import isclose
from math import log
from math import log2
from math import sqrt
from typing import DefaultDict
from typing import List
from typing import NamedTuple
from typing import Tuple

from coinflip._randtests.common.collections import FloorDict
from coinflip._randtests.common.core import *
from coinflip._randtests.common.exceptions import TestNotImplementedError
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.testutils import rawblocks
from coinflip._randtests.common.typing import Face
from coinflip._randtests.common.typing import Integer

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
    blocksize: Integer
    init_nblocks: Integer


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


@randtest(min_n=4)
def maurers_universal(series, heads, tails, ctx, blocksize=None, init_nblocks=None):
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
    init_series, segment_series = series[:init_n], series[init_n:]
    segment_nblocks = (n - init_n) // blocksize

    mean_expect, variance = blocksize_dists[blocksize]

    set_task_total(ctx, init_nblocks + segment_nblocks + 2)

    failures = check_recommendations(
        ctx,
        {
            "n ≥ 387840": n >= 387840,
            "6 ≤ blocksize ≤ 16": 6 <= blocksize <= 16,
            "init_nblocks ≈ 10 * 2 ** segment_nblocks": intclose(
                init_nblocks, 10 * 2 ** segment_nblocks
            ),
            "segment_nblocks ≈ ⌈n / blocksize⌉ - init_nblocks": isclose(
                segment_nblocks, floor(n / blocksize) - init_nblocks
            ),
        },
    )

    permutation_last_init_pos = defaultdict(int)

    init_blocks = rawblocks(init_series, blocksize)
    for pos, permutation in enumerate(init_blocks, 1):
        permutation_last_init_pos[permutation] = pos

        advance_task(ctx)

    segment_blocks = rawblocks(segment_series, blocksize)
    permutation_positions = defaultdict(list)
    segment_firstpos = init_nblocks + 1
    for pos, permutation in enumerate(segment_blocks, segment_firstpos):
        permutation_positions[permutation].append(pos)

        advance_task(ctx)

    distances_total = 0
    for permutation, positions in permutation_positions.items():
        last_occurence = permutation_last_init_pos[permutation]
        for pos in positions:
            distance = pos - last_occurence
            distances_total += log2(distance)

            last_occurence = pos

    advance_task(ctx)

    statistic = distances_total / segment_nblocks

    normdiff = abs((statistic - mean_expect) / (sqrt(2 * variance)))
    p = erfc(normdiff)

    advance_task(ctx)

    return UniversalTestResult(
        heads,
        tails,
        failures,
        statistic,
        p,
        blocksize,
        init_nblocks,
        segment_nblocks,
        permutation_last_init_pos,
        permutation_positions,
    )


@dataclass
class UniversalTestResult(TestResult):
    blocksize: Integer
    init_nblocks: Integer
    segment_nblocks: Integer
    permutation_last_init_pos: DefaultDict[Tuple[Face, ...], Integer]
    permutation_positions: DefaultDict[Tuple[Face, ...], List[Integer]]

    def _render(self):
        yield self._pretty_result("log2 distances")

        yield TestResult._pretty_inputs(
            ("init nblocks", self.init_nblocks),
            ("segment nblocks", self.segment_nblocks),
        )

        # TODO maybe use this table for a verbose option or something (it's huge)
        # table = make_testvars_table("permutation", "init pos", "test positions", justify=False)
        # for permutation, positions in self.permutation_positions.items():
        #     f_permutation = pretty_subseq(permutation, self.heads, self.tails)

        #     init_pos = self.permutation_last_init_pos[permutation]
        #     f_init_pos = str(init_pos)

        #     f_positions = ", ".join(str(pos) for pos in positions)

        #     table.add_row(f_permutation, f_init_pos, f_positions)


def intclose(int1, int2, abs_tol=5):
    return abs(int1 - int2) <= abs_tol
