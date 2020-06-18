from functools import wraps
from math import exp

import pandas as pd
from scipy.special import gammaincc
from scipy.special import hyp1f1

from rngtest.stattests._common import TestResult
from rngtest.stattests._common import rawchunks
from rngtest.stattests._common import stattest

__all__ = ["non_overlapping_template_matching", "overlapping_template_matching"]


class TemplateContainsElementsNotInSequenceError(ValueError):
    pass


def template(func):
    @wraps(func)
    def wrapper(series: pd.Series, template, *args, **kwargs):
        if not isinstance(template, pd.Series):
            template = pd.Series(template)

        for value in template.unique():
            if value not in series.unique():
                raise TemplateContainsElementsNotInSequenceError()

        # TODO Generate template

        result = func(series, template, *args, **kwargs)

        return result

    return wrapper


@stattest
@template
def non_overlapping_template_matching(series, template, nblocks=968):
    """Matches of template per block is compared to expected result

    The sequence is split into blocks, where the number of non-overlapping
    matches to the template in each block is found. This is referenced to the
    expected mean and variance in matches of a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    template : array-like
        Template to match with the sequence
    nblocks : int
        Number of blocks to split sequence into

    Returns
    -------
    TestResult
        Dataclass that contains the test's statistic and p-value.

    Raises
    ------
    TemplateContainsElementsNotInSequenceError
        If template contains values not present in sequence
    """
    n = len(series)
    blocksize = n // nblocks

    template_size = len(template)
    raw_template = template.values

    block_matches = []
    for rawchunk in rawchunks(series, blocksize=blocksize):
        matches = 0
        pointer = 0

        boundary = len(rawchunk) - template_size
        while pointer < boundary:
            window = rawchunk[pointer : pointer + template_size]

            if all(x == y for x, y in zip(window, raw_template)):
                matches += 1
                pointer += template_size
            else:
                pointer += 1

        block_matches.append(matches)

    mean_expected = (blocksize - template_size + 1) / 2 ** template_size
    variance_expected = blocksize * (
        (1 / 2 ** template_size) - ((2 * template_size - 1)) / 2 ** (2 * template_size)
    )

    statistic = (
        sum((matches - mean_expected) ** 2 for matches in block_matches)
        / variance_expected
    )
    p = gammaincc(nblocks / 2, statistic / 2)

    return TestResult(statistic=statistic, p=p)


@stattest
@template
def overlapping_template_matching(series, template, nblocks=8):
    """Overlapping matches of template per block is compared to expected result

    The sequence is split into blocks, where the number of overlapping matches
    to the template in each block is found. This is referenced to the expected
    mean and variance in matches of a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    template : array-like
        Template to match with the sequence
    nblocks : int
        Number of blocks to split sequence into

    Returns
    -------
    TestResult
        Dataclass that contains the test's statistic and p-value.

    Raises
    ------
    TemplateContainsElementsNotInSequenceError
        If template contains values not present in sequence
    """
    n = len(series)
    blocksize = n // nblocks

    template_size = len(template)
    raw_template = template.values

    block_matches = []
    for rawchunk in rawchunks(series, blocksize=blocksize):
        matches = 0

        for pointer in range(blocksize):
            window = rawchunk[pointer : pointer + template_size]

            if all(x == y for x, y in zip(window, raw_template)):
                matches += 1

        block_matches.append(matches)

    tallies = [0 for _ in range(6)]
    for matches in block_matches:
        i = min(matches, 5)
        tallies[i] += 1

    lambda_ = (blocksize - template_size + 1) / 2 ** template_size
    eta = lambda_ / 2

    probabilities = [
        ((eta * exp(-2 * eta)) / 2 ** x) * hyp1f1(x + 1, 2, eta)
        for x in range(len(tallies))
    ]

    statistic = sum(
        (tally - nblocks * probability) ** 2 / (nblocks * probability)
        for tally, probability in zip(tallies, probabilities)
    )

    df = len(tallies) - 1
    p = gammaincc(df / 2, statistic / 2)

    return TestResult(statistic=statistic, p=p)
