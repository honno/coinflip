from collections import Counter
from dataclasses import dataclass
from functools import wraps
from math import exp
from math import floor
from math import sqrt
from random import choice
from typing import List
from warnings import warn

import pandas as pd
from scipy.special import gammaincc
from scipy.special import hyp1f1
from tabulate import tabulate

from rngtest.stattests._common import TestResult
from rngtest.stattests._common import rawblocks
from rngtest.stattests._common import stattest

__all__ = ["non_overlapping_template_matching", "overlapping_template_matching"]


# ------------------------------------------------------------------------------
# Template decorator for type checking and defaults


class TemplateContainsElementsNotInSequenceError(ValueError):
    pass


def template(func):
    @wraps(func)
    def wrapper(series: pd.Series, template=None, *args, **kwargs):
        values = series.unique()

        if template is None:
            n = len(series)
            template_size = min(floor(sqrt(n)), 9)
            template = pd.Series(choice(values) for _ in range(template_size))

        else:
            if not isinstance(template, pd.Series):
                template = pd.Series(template)

            for value in template.unique():
                if value not in values:
                    raise TemplateContainsElementsNotInSequenceError()

        result = func(series, template, *args, **kwargs)

        return result

    return wrapper


# ------------------------------------------------------------------------------
# Non-overlapping Template Matching Test


@stattest(min_input=288)  # template_size=9, nblocks=8, blocksize=4*template_size
@template
def non_overlapping_template_matching(series, template, nblocks=8):
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

    recommendations = {
        "nblocks <= 100": nblocks <= 100,
        "blocksize > 0.01 * n": blocksize > 0.01 * n,
        "nblocks == n // blocksize": nblocks == n // blocksize,
    }
    for rec, success in recommendations.items():
        if not success:
            warn(f"Input parameters fail recommendation {rec}", UserWarning)

    matches_expect = (blocksize - template_size + 1) / 2 ** template_size
    variance = blocksize * (
        (1 / 2 ** template_size) - ((2 * template_size - 1)) / 2 ** (2 * template_size)
    )

    template_tup = template.values

    block_matches = []
    for block_tup in rawblocks(series, blocksize=blocksize):
        matches = 0
        pointer = 0

        boundary = blocksize - template_size
        while pointer < boundary:
            window = block_tup[pointer : pointer + template_size]

            if all(x == y for x, y in zip(window, template_tup)):
                matches += 1
                pointer += template_size
            else:
                pointer += 1

        block_matches.append(matches)

    match_diffs = [matches - matches_expect for matches in block_matches]

    statistic = sum(diff ** 2 / variance for diff in match_diffs)
    p = gammaincc(nblocks / 2, statistic / 2)

    return NonOverlappingTemplateMatchingTestResult(
        statistic=statistic,
        p=p,
        template=template,
        matches_expect=matches_expect,
        variance=variance,
        block_matches=block_matches,
        match_diffs=match_diffs,
    )


@dataclass
class NonOverlappingTemplateMatchingTestResult(TestResult):
    template: pd.Series
    matches_expect: float
    variance: float
    block_matches: List[int]
    match_diffs: List[float]

    def __str__(self):
        f_stats = self.stats_table("chi-square")

        f_template = self.template.values
        f_matches_expect = round(self.matches_expect, 1)

        matches_count = Counter(self.block_matches)

        table = []
        for matches, count in sorted(matches_count.items()):
            diff = matches - self.matches_expect
            f_diff = round(diff, 1)
            table.append([matches, f_diff, count])

        f_table = tabulate(table, headers=["matches", "diff", "nblocks"])

        return (
            f"{f_stats}\n"
            "\n"
            f"template: {f_template}\n"
            f"expected matches per block: {f_matches_expect}\n"
            "\n"
            f"{f_table}"
        )


# ------------------------------------------------------------------------------
# Overlapping Template Matching Test


matches_ceil = 5


# TODO fix probabilities
@stattest()
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
    template_tup = tuple(template.tolist())

    lambda_ = (blocksize - template_size + 1) / 2 ** template_size
    eta = lambda_ / 2

    first_prob = exp(-eta)
    probabilities = [first_prob]
    for matches in range(1, matches_ceil):
        prob = ((eta * exp(-2 * eta)) / 2 ** matches) * hyp1f1(matches + 1, 2, eta)
        probabilities.append(prob)
    last_prob = 1 - sum(probabilities)
    probabilities.append(last_prob)

    expected_tallies = [prob * nblocks for prob in probabilities]

    block_matches = []
    for block_tup in rawblocks(series, blocksize=blocksize):
        matches = 0

        boundary = blocksize - template_size
        for pointer in range(boundary + 1):
            window = block_tup[pointer : pointer + template_size]

            if all(x == y for x, y in zip(window, template_tup)):
                matches += 1

        block_matches.append(matches)

    tallies = [0 for _ in range(matches_ceil + 1)]
    for matches in block_matches:
        i = min(matches, 5)
        tallies[i] += 1

    reality_check = []
    for tally_expect, tally in zip(expected_tallies, tallies):
        diff = (tally - tally_expect) ** 2 / tally_expect
        reality_check.append(diff)

    statistic = sum(reality_check)

    p = gammaincc(matches_ceil / 2, statistic / 2)  # TODO should first param be df / 2

    return OverlappingTemplateMatchingTestResult(
        statistic=statistic,
        p=p,
        template=template,
        expected_tallies=expected_tallies,
        tallies=tallies,
    )


@dataclass
class OverlappingTemplateMatchingTestResult(TestResult):
    template: pd.Series
    expected_tallies: List[int]
    tallies: List[int]

    def __post_init__(self):
        self.tally_diffs = []
        for expect, actual in zip(self.expected_tallies, self.tallies):
            diff = actual - expect
            self.tally_diffs.append(diff)

    def __str__(self):
        f_stats = self.stats_table("chi-square")

        f_template = self.template.values

        f_matches = [f"{x}" for x in range(matches_ceil + 1)]
        f_matches[-1] = f"{f_matches[-1]}+"

        f_expected_tallies = [round(tally, 1) for tally in self.expected_tallies]
        f_diffs = [round(diff, 1) for diff in self.tally_diffs]

        f_table = tabulate(
            zip(f_matches, self.tallies, f_expected_tallies, f_diffs),
            headers=["matches", "count", "expected", "diff"],
        )

        return f"{f_stats}\n" "\n" f"template: {f_template}\n" "\n" f"{f_table}"
