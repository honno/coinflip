from math import exp
from typing import List

import pandas as pd
from scipy.special import gammaincc
from scipy.special import hyp1f1

from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest
from rngtest.stattests.common import chunks

__all__ = ["non_overlapping_template_matching", "overlapping_template_matching"]


class TemplateContainsElementsNotInSeriesError(ValueError):
    pass


def template(func):
    def wrapper(series: pd.Series, template: List, *args, **kwargs):
        if not isinstance(template, pd.Series):
            template = pd.Series(template)

        for value in template.unique():
            if value not in series.unique():
                raise TemplateContainsElementsNotInSeriesError()

        result = func(series, template, *args, **kwargs)

        return result

    return wrapper


@binary_stattest
@template
def non_overlapping_template_matching(series, template, nblocks=968):
    n = len(series)
    blocksize = n // nblocks

    templatesize = len(template)

    matches_per_block = []
    for chunk in chunks(series, blocksize=blocksize):
        matches = 0
        pointer = 0

        while pointer < len(chunk) - templatesize:
            window = chunk[pointer : pointer + templatesize]
            if all(x == y for x, y in zip(window.values, template.values)):
                matches += 1
                pointer += templatesize
            else:
                pointer += 1

        matches_per_block.append(matches)

    theoretical_mean = (blocksize - templatesize + 1) / 2 ** templatesize
    theoretical_variance = blocksize * (
        (1 / 2 ** templatesize) - ((2 * templatesize - 1)) / 2 ** (2 * templatesize)
    )

    # mean = (blocksize - templatesize + 1) / 2**templatesize
    # variance = sum((matches - mean)**2 for matches in matches_per_block) / nblocks

    statistic = (
        sum((matches - theoretical_mean) ** 2 for matches in matches_per_block)
        / theoretical_variance
    )
    p = gammaincc(nblocks / 2, statistic / 2)

    return TestResult(statistic=statistic, p=p)


@binary_stattest
@template
def overlapping_template_matching(series, template, nblocks=8):
    if not isinstance(template, pd.Series):
        template = pd.Series(template)

    n = len(series)
    blocksize = n // nblocks

    templatesize = len(template)

    matches_per_block = []
    for chunk in chunks(series, blocksize=blocksize):
        matches = 0

        for i in range(blocksize):
            window = chunk[i : i + templatesize]

            if all(x == y for x, y in zip(window.values, template.values)):
                matches += 1

        matches_per_block.append(matches)

    tally_table = [0 for _ in range(6)]
    for matches in matches_per_block:
        if matches >= 5:
            tally_table[5] += 1
        else:
            tally_table[matches] += 1

    lambda_ = (blocksize - templatesize + 1) / 2 ** templatesize
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
