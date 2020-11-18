from collections import Counter
from collections import defaultdict
from itertools import accumulate
from itertools import product
from math import erfc
from math import floor
from math import log
from math import log2
from math import sqrt
from typing import Iterator
from typing import List
from typing import Tuple

import numpy as np
from more_itertools import chunked
from more_itertools import split_at
from more_itertools import windowed
from scipy.fft import fft
from scipy.special import gammaincc
from scipy.stats import chisquare
from scipy.stats import norm
from typing_extensions import Literal

from coinflip.algorithms import berlekamp_massey
from coinflip.algorithms import matrix_rank
from coinflip.collections import Bins
from coinflip.collections import FloorDict
from coinflip.collections import defaultlist

__all__ = [
    "monobit",
    "frequency_within_block",
    "runs",
    "longest_runs",
    "binary_matrix_rank",
    "spectral",
    "non_overlapping_template_matching",
    "overlapping_template_matching",
    "maurers_universal",
    "linear_complexity",
    "serial",
    "approximate_entropy",
    "cusum",
    "random_excursions",
    "random_excursions_variant",
]


def monobit(sequence: List[Literal[0, 1]]):
    n = len(sequence)

    ones = sum(1 for bit in sequence if bit == 1)
    zeroes = n - ones
    diff = abs(ones - zeroes)

    normdiff = diff / sqrt(n)
    p = erfc(normdiff / sqrt(2))

    return normdiff, p


def frequency_within_block(sequence: List[Literal[0, 1]], blocksize: int):
    n = len(sequence)
    nblocks = n // blocksize

    deviations = []
    for block in chunked(sequence, blocksize):
        ones = sum(1 for bit in block if bit == 1)
        prop = ones / blocksize
        dev = prop - 1 / 2
        deviations.append(dev)

    chi2 = 4 * blocksize * sum(x ** 2 for x in deviations)
    p = gammaincc(nblocks / 2, chi2 / 2)

    return chi2, p


def runs(sequence: List[Literal[0, 1]]):
    n = len(sequence)

    ones = sum(1 for bit in sequence if bit == 1)

    prop_ones = ones / n
    prop_zeroes = 1 - prop_ones

    nruns = sum(1 for _ in asruns(sequence))
    p = erfc(
        abs(nruns - (2 * ones * prop_zeroes))
        / (2 * sqrt(2 * n) * prop_ones * prop_zeroes)
    )

    return nruns, p


def longest_runs(sequence: List[Literal[0, 1]]):
    n_defaults = FloorDict(
        {
            128: (8, 16, [1, 2, 3, 4]),
            6272: (128, 49, [4, 5, 6, 7, 8, 9]),
            750000: (10 ** 4, 75, [10, 11, 12, 13, 14, 15, 16]),
        }
    )
    n = len(sequence)
    blocksize, nblocks, intervals = n_defaults[n]
    maxlen_bins = Bins(intervals)

    blocksize_probabilities = {
        8: [0.2148, 0.3672, 0.2305, 0.1875],
        128: [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124],
        512: [0.1170, 0.2460, 0.2523, 0.1755, 0.1027, 0.1124],
        1000: [0.1307, 0.2437, 0.2452, 0.1714, 0.1002, 0.1088],
        10000: [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727],
    }
    probabilities = blocksize_probabilities[blocksize]
    expected_bincounts = [prob * nblocks for prob in probabilities]

    boundary = nblocks * blocksize
    for block in chunked(sequence[:boundary], blocksize):
        one_run_lengths = [length for value, length in asruns(block) if value == 1]

        try:
            maxlen = max(one_run_lengths)
        except ValueError:
            maxlen = 0

        maxlen_bins[maxlen] += 1

    chi2, p = chisquare(list(maxlen_bins.values()), expected_bincounts)

    return chi2, p


def binary_matrix_rank(sequence: List[Literal[0, 1]], matrix_dimen: Tuple[int, int]):
    n = len(sequence)
    nrows, ncols = matrix_dimen
    blocksize = nrows * ncols
    nblocks = n // blocksize
    trunc_sequence = sequence[: nblocks * blocksize]

    expected_rankcounts = (0.2888 * nblocks, 0.5776 * nblocks, 0.1336 * nblocks)

    ranks = []
    for block in chunked(trunc_sequence, blocksize):
        matrix = chunked(block, ncols)
        rank = matrix_rank(matrix)
        ranks.append(rank)

    fullrank = min(nrows, ncols)
    rankcounts = [0 for _ in range(3)]
    for rank in ranks:
        if rank == fullrank:
            rankcounts[0] += 1
        elif rank == fullrank - 1:
            rankcounts[1] += 1
        else:
            rankcounts[2] += 1

    chi2, p = chisquare(rankcounts, expected_rankcounts)

    return chi2, p


def spectral(sequence: List[Literal[0, 1]]):
    n = len(sequence)
    if n % 2 != 0:
        sequence = sequence[:-1]

    threshold = sqrt(log(1 / 0.05) * n)
    nbelow_expect = 0.95 * n / 2

    oscillations = [bit if bit == 1 else -1 for bit in sequence]
    fourier = fft(oscillations)
    half_fourier = fourier[: n // 2]

    peaks = [abs(complex_num) for complex_num in half_fourier]
    nbelow = sum(peak < threshold for peak in peaks)

    diff = nbelow - nbelow_expect
    normdiff = diff / sqrt((n * 0.95 * 0.05) / 4)
    p = erfc(abs(normdiff) / sqrt(2))

    return normdiff, p


def non_overlapping_template_matching(
    sequence: List[Literal[0, 1]], template_size: int, blocksize: int
):
    n = len(sequence)
    nblocks = n // blocksize

    matches_expect = (blocksize - template_size + 1) / 2 ** template_size
    variance = blocksize * (
        (1 / 2 ** template_size) - ((2 * template_size - 1)) / 2 ** (2 * template_size)
    )

    template_block_matches = defaultdict(lambda: defaultlist(int))
    for i, block in enumerate(chunked(sequence, blocksize)):
        matches = defaultdict(int)

        for window in windowed(block, template_size):
            matches[window] += 1

        for template, matches in matches.items():
            template_block_matches[template][i] = matches

    statistics = []
    pvalues = []
    for template in product([0, 1], repeat=template_size):
        block_matches = template_block_matches[template][:nblocks]
        match_diffs = [matches - matches_expect for matches in block_matches]

        chi2 = sum(diff ** 2 / variance for diff in match_diffs)
        p = gammaincc(nblocks / 2, chi2 / 2)

        statistics.append(chi2)
        pvalues.append(p)

    return statistics, pvalues


def overlapping_template_matching(
    sequence: List[Literal[0, 1]], template_size: int, blocksize: int
):
    n = len(sequence)
    template = [1 for _ in range(template_size)]
    nblocks = n // blocksize
    trunc_sequence = sequence[: nblocks * blocksize]

    probabilities = [0.367879, 0.183939, 0.137954, 0.099634, 0.069935, 0.140656]
    expected_tallies = [prob * nblocks for prob in probabilities]

    block_matches = []
    for block in chunked(trunc_sequence, blocksize):
        matches = 0

        for window in windowed(block, template_size):
            if all(wbit == tbit for wbit, tbit in zip(window, template)):
                matches += 1

        block_matches.append(matches)

    tallies = [0 for _ in range(6)]
    for matches in block_matches:
        i = min(matches, 5)
        tallies[i] += 1

    chi2, p = chisquare(tallies, expected_tallies)

    return chi2, p


def maurers_universal(sequence: List[Literal[0, 1]], blocksize: int, init_nblocks: int):
    n = len(sequence)
    nblocks = n // blocksize
    segment_nblocks = nblocks - init_nblocks

    boundary = init_nblocks * blocksize
    init_sequence = sequence[:boundary]
    test_sequence = sequence[boundary : nblocks * blocksize]

    blocksize_dists = {
        1: (0.7326495, 0.690),
        2: (1.5374383, 1.338),
        3: (2.4016068, 1.901),
        4: (3.3112247, 2.358),
        5: (4.2534266, 2.705),
        6: (5.2177052, 2.954),
        7: (6.1962507, 3.125),
        8: (7.1836656, 3.238),
        9: (8.1764248, 3.311),
        10: (9.1723243, 3.356),
        11: (10.170032, 3.384),
        12: (11.168765, 3.401),
        13: (12.168070, 3.410),
        14: (13.167693, 3.416),
        15: (14.167488, 3.419),
        16: (15.167379, 3.421),
    }
    mean_expect, variance = blocksize_dists[blocksize]

    last_permutation_pos = defaultdict(int)
    for pos, permutation in enumerate(chunked(init_sequence, blocksize), 1):
        last_permutation_pos[tuple(permutation)] = pos

    log2_distances = 0
    for pos, permutation in enumerate(
        chunked(test_sequence, blocksize), init_nblocks + 1
    ):
        distance = pos - last_permutation_pos[tuple(permutation)]
        log2_distances += log2(distance)

        last_permutation_pos[tuple(permutation)] = pos

    norm_distances = log2_distances / segment_nblocks
    p = erfc(abs((norm_distances - mean_expect) / (sqrt(2 * variance))))

    return norm_distances, p


def serial(sequence: List[Literal[0, 1]], blocksize: int):
    n = len(sequence)

    normalised_sums = {}
    for window_size in [blocksize, blocksize - 1, blocksize - 2]:
        if window_size > 0:
            head = sequence[: window_size - 1]
            ouroboros = sequence + head

            counts = defaultdict(int)
            for window in windowed(ouroboros, window_size):
                counts[tuple(window)] += 1

            sum_squares = sum(count ** 2 for count in counts.values())
            normsum = (2 ** window_size / n) * sum_squares - n

        else:
            normsum = 0

        normalised_sums[window_size] = normsum

    normsum_deltas = [
        normalised_sums[blocksize] - normalised_sums[blocksize - 1],
        normalised_sums[blocksize]
        - 2 * normalised_sums[blocksize - 1]
        + normalised_sums[blocksize - 2],
    ]

    pvalues = [
        gammaincc(2 ** (blocksize - 2), normsum_deltas[0] / 2),
        gammaincc(2 ** (blocksize - 3), normsum_deltas[1] / 2),
    ]

    return normsum_deltas, pvalues


def linear_complexity(sequence: List[Literal[0, 1]], blocksize: int):
    n = len(sequence)
    nblocks = n // blocksize
    trunc_sequence = sequence[: nblocks * blocksize]

    probabilities = [0.010417, 0.03125, 0.125, 0.5, 0.25, 0.0625, 0.020833]
    mean_expect = (
        blocksize / 2
        + (9 + (-(1 ** (blocksize + 1)))) / 36
        - (blocksize / 3 + 2 / 9) / 2 ** blocksize
    )
    expected_bincounts = [nblocks * prob for prob in probabilities]

    variance_bins = Bins([-3, -2, -1, 0, 1, 2, 3])
    for block in chunked(trunc_sequence, blocksize):
        linear_complexity = berlekamp_massey(block)
        variance = (-1) ** blocksize * (linear_complexity - mean_expect) + 2 / 9
        variance_bins[variance] += 1

    chi2, p = chisquare(list(variance_bins.values()), expected_bincounts)

    return chi2, p


def approximate_entropy(sequence: List[Literal[0, 1]], blocksize: int):
    n = len(sequence)

    phis = []
    for template_size in [blocksize, blocksize + 1]:
        head = sequence[: template_size - 1]
        ouroboros = sequence + head

        permutation_counts = defaultdict(int)
        for window in windowed(ouroboros, template_size):
            permutation_counts[tuple(window)] += 1

        normalised_counts = []
        for count in permutation_counts.values():
            normcount = count / n
            normalised_counts.append(normcount)

        phi = sum(normcount * log(normcount) for normcount in normalised_counts)
        phis.append(phi)

    approx_entropy = phis[0] - phis[1]
    chi2 = 2 * n * (log(2) - approx_entropy)
    p = gammaincc(2 ** (blocksize - 1), chi2 / 2)

    return chi2, p


def cusum(sequence: List[Literal[0, 1]], reverse: bool = False):
    n = len(sequence)

    oscillations = [bit if bit == 1 else -1 for bit in sequence]
    if reverse:
        oscillations = oscillations[::-1]
    cusums = accumulate(oscillations)

    abs_cusums = [abs(cusum) for cusum in cusums]
    max_cusum = max(abs_cusums)

    p = (
        1
        - sum(
            norm.cdf((4 * k + 1) * max_cusum / sqrt(n))
            - norm.cdf((4 * k - 1) * max_cusum / sqrt(n))
            for k in np.arange(
                floor((-n / max_cusum + 1) / 4), floor((n / max_cusum - 1) / 4) + 1, 1
            )
        )
        + sum(
            norm.cdf((4 * k + 3) * max_cusum / sqrt(n))
            - norm.cdf((4 * k + 1) * max_cusum / sqrt(n))
            for k in np.arange(
                floor((-n / max_cusum - 3) / 4), floor((n / max_cusum - 1) / 4) + 1, 1
            )
        )
    )

    return max_cusum, p


def random_excursions(sequence: List[Literal[0, 1]]):
    states = [-4, -3, -2, -1, 1, 2, 3, 4]
    state_count_bins = {state: Bins(range(6)) for state in states}

    state_probabilities = {
        1: [0.5000, 0.2500, 0.1250, 0.0625, 0.0312, 0.0312],
        2: [0.7500, 0.0625, 0.0469, 0.0352, 0.0264, 0.0791],
        3: [0.8333, 0.0278, 0.0231, 0.0193, 0.0161, 0.0804],
        4: [0.8750, 0.0156, 0.0137, 0.0120, 0.0105, 0.0733],
        5: [0.9000, 0.0100, 0.0090, 0.0081, 0.0073, 0.0656],
        6: [0.9167, 0.0069, 0.0064, 0.0058, 0.0053, 0.0588],
        7: [0.9286, 0.0051, 0.0047, 0.0044, 0.0041, 0.0531],
    }

    oscillations = [bit if bit == 1 else -1 for bit in sequence]
    cusums = accumulate(oscillations)

    ncycles = 0
    for cycle in split_at(cusums, lambda x: x == 0):
        ncycles += 1

        counts = Counter(cycle)
        for state in states:
            count = counts[state]
            state_count_bins[state][count] += 1

    statistics = []
    pvalues = []
    for state in states:
        probabilities = state_probabilities[abs(state)]
        expected_bincounts = [ncycles * prob for prob in probabilities]

        bincounts = state_count_bins[state].values()

        chi2, p = chisquare(list(bincounts), expected_bincounts)

        statistics.append(chi2)
        pvalues.append(p)

    return statistics, pvalues


def random_excursions_variant(sequence: List[Literal[0, 1]]):
    states = [-9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    oscillations = [bit if bit == 1 else -1 for bit in sequence]
    cusums = accumulate(oscillations)

    state_counts = Counter(cusums)
    ncycles = state_counts[0] + 1

    counts = []
    pvalues = []
    for state in states:
        count = state_counts[state]
        p = erfc(abs(count - ncycles) / sqrt(2 * ncycles * (4 * abs(state) - 2)))

        counts.append(count)
        pvalues.append(p)

    return counts, pvalues


# ------------------------------------------------------------------------------
# Helpers


def asruns(sequence: List[Literal[0, 1]]) -> Iterator[Tuple[Literal[0, 1], int]]:
    run_val = sequence[0]
    run_len = 1

    for value in sequence[1:]:
        if value == run_val:
            run_len += 1

        else:
            yield run_val, run_len

            run_val = value
            run_len = 1

    yield run_val, run_len
