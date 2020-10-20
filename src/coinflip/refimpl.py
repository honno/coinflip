from collections import defaultdict
from itertools import product
from math import erfc
from math import log
from math import log2
from math import sqrt
from typing import Iterator
from typing import Sequence
from typing import Tuple

from more_itertools import chunked
from more_itertools import windowed
from scipy.fft import fft
from scipy.special import gammaincc
from scipy.stats import chisquare
from typing_extensions import Literal

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
    # "linear_complexity",
    # "serial",
    # "approximate_entropy",
    # "cusum",
    # "random_excursions",
    # "random_excursions_variant",
]

Bit = Literal[0, 1]


def monobit(sequence: Sequence[Bit]):
    n = len(sequence)

    ones = sum(1 for bit in sequence if bit == 1)
    zeroes = n - ones
    diff = abs(ones - zeroes)

    normdiff = diff / sqrt(n)
    p = erfc(normdiff / sqrt(2))

    return normdiff, p


def frequency_within_block(sequence: Sequence[Bit], blocksize: int):
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


def runs(sequence: Sequence[Bit]):
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


def longest_runs(sequence: Sequence[Bit]):
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


def binary_matrix_rank(sequence: Sequence[Bit], matrix_dimen: Tuple[int, int]):
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

    statistic, p = chisquare(rankcounts, expected_rankcounts)

    return statistic, p


def spectral(sequence: Sequence[Bit]):
    n = len(sequence)

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
    sequence: Sequence[Bit], template_size: int, blocksize: int
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

        statistic = sum(diff ** 2 / variance for diff in match_diffs)
        p = gammaincc(nblocks / 2, statistic / 2)

        statistics.append(statistic)
        pvalues.append(p)

    return statistics, pvalues


def overlapping_template_matching(
    sequence: Sequence[Bit], template_size: int, blocksize: int
):
    n = len(sequence)
    template = [1 for _ in range(template_size)]
    nblocks = n // blocksize
    trunc_sequence = sequence[: nblocks * blocksize]

    probabilities = [0.364091, 0.185659, 0.139381, 0.100571, 0.0704323, 0.139865]
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

    statistic, p = chisquare(tallies, expected_tallies)

    return statistic, p


def maurers_universal(sequence: Sequence[Bit], blocksize: int, init_nblocks: int):
    n = len(sequence)
    nblocks = n // blocksize
    segment_nblocks = nblocks - init_nblocks

    boundary = init_nblocks * blocksize
    init_sequence = sequence[:boundary]
    segment_sequence = sequence[boundary : nblocks * blocksize]

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

    distances_total = 0
    for pos, permutation in enumerate(
        chunked(segment_sequence, blocksize), init_nblocks + 1
    ):
        distance = pos - last_permutation_pos[tuple(permutation)]
        distances_total += log2(distance)

        last_permutation_pos[tuple(permutation)] = pos

    statistic = distances_total / segment_nblocks
    p = erfc(abs((statistic - mean_expect) / (sqrt(2 * variance))))

    return statistic, p


# def serial(sequence: Sequence[Bit], blocksize: int):
#     n = len(sequence)


# def linear_complexity(sequence: Sequence[Bit], blocksize: int):
#     n = len(sequence)


# def approximate_entropy(sequence: Sequence[Bit], blocksize: int):
#     n = len(sequence)


# def cusum(sequence: Sequence[Bit], reverse: bool = False):
#     n = len(sequence)


# def random_excursions(sequence: Sequence[Bit]):
#     n = len(sequence)


# def random_excursions_variant(sequence: Sequence[Bit]):
#     n = len(sequence)


# ------------------------------------------------------------------------------
# Helpers


def asruns(sequence: Sequence[Bit]) -> Iterator[Tuple[Bit, int]]:
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
