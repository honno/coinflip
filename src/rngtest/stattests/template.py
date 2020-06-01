from itertools import combinations
from math import exp

from scipy.special import gammaincc
from scipy.special import hyp1f1

from rngtest.stattests.common.decorators import binary_stattest
from rngtest.stattests.common.methods import chunks
from rngtest.stattests.common.result import TestResult

__all__ = ["non_overlapping_template_matching", "overlapping_template_matching"]


@binary_stattest
def non_overlapping_template_matching(series, template=None, nblocks=968):
    n = len(series)
    block_size = n // nblocks

    if template is None:
        possible_templates = combinations(series.unique(), block_size)
        template = next(possible_templates)
    template_size = len(template)

    matches_per_block = []
    for chunk in chunks(series, block_size=block_size):
        matches = 0
        pointer = 0

        while pointer < len(chunk) - template_size:
            window = chunk[pointer : pointer + template_size]
            if all(x == y for x, y in zip(window.values, template.values)):
                matches += 1
                pointer += template_size
            else:
                pointer += 1

        matches_per_block.append(matches)

    theoretical_mean = (block_size - template_size + 1) / 2 ** template_size
    theoretical_variance = block_size * (
        (1 / 2 ** template_size) - ((2 * template_size - 1)) / 2 ** (2 * template_size)
    )

    # mean = (block_size - template_size + 1) / 2**template_size
    # variance = sum((matches - mean)**2 for matches in matches_per_block) / nblocks

    statistic = (
        sum((matches - theoretical_mean) ** 2 for matches in matches_per_block)
        / theoretical_variance
    )
    p = gammaincc(nblocks / 2, statistic / 2)

    return TestResult(statistic=statistic, p=p)


@binary_stattest
def overlapping_template_matching(series, template=None, nblocks=8):
    n = len(series)
    block_size = n // nblocks

    if template is None:
        possible_templates = combinations(series.unique(), block_size)
        template = next(possible_templates)
    template_size = len(template)

    matches_per_block = []
    for chunk in chunks(series, block_size=block_size):
        matches = 0

        for i in range(block_size):
            window = chunk[i : i + template_size]

            if all(x == y for x, y in zip(window.values, template.values)):
                matches += 1

        matches_per_block.append(matches)

    tally_table = [0 for _ in range(6)]
    for matches in matches_per_block:
        if matches >= 5:
            tally_table[5] += 1
        else:
            tally_table[matches] += 1

    lambda_ = (block_size - template_size + 1) / 2 ** template_size
    eta = lambda_ / 2

    probabilities = [
        ((eta * exp(-2 * eta)) / 2 ** x) * hyp1f1(x + 1, 2, eta) for x in range(6)
    ]

    statistic = sum(
        (tally - nblocks * probability) ** 2 / (nblocks * probability)
        for tally, probability in zip(tally_table, probabilities)
    )
    p = gammaincc(5 / 2, statistic / 2)

    return TestResult(statistic=statistic, p=p)
