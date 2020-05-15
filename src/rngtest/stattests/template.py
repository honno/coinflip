from itertools import combinations

from scipy.special import gammaincc

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks

__all__ = ["non_overlapping_template_matching"]


@binary_stattest
def non_overlapping_template_matching(series, template=None, nblocks=8):
    n = len(series)
    block_size = n // nblocks

    if template is None:
        all_templates = combinations(series.unique(), block_size)
        template = next(all_templates)
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
