from collections import Counter
from dataclasses import dataclass
from math import exp
from math import floor
from math import isclose
from math import log2
from math import sqrt
from random import choice
from typing import List

from scipy.special import gammaincc
from scipy.special import hyp1f1
from tabulate import tabulate

from rngtest.stattests._decorators import stattest
from rngtest.stattests._result import TestResult
from rngtest.stattests._testutils import check_recommendation
from rngtest.stattests._testutils import rawblocks

__all__ = ["non_overlapping_template_matching", "overlapping_template_matching"]


def make_template(series, blocksize):
    template_size = min(max(floor(sqrt(blocksize)), 2), 12)

    values = series.unique()
    template = [choice(values) for _ in range(template_size)]

    return template


# ------------------------------------------------------------------------------
# Non-overlapping Template Matching Test


@stattest(rec_input=288)  # template_size=9, nblocks=8, blocksize=4*template_size
def non_overlapping_template_matching(series, template: List = None, nblocks=None):
    """Matches of template per block is compared to expected result

    The sequence is split into blocks, where the number of non-overlapping
    matches to the template in each block is found. This is referenced to the
    expected mean and variance in matches of a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    template : Tuple, optional
        Template to match with the sequence, randomly generated if not
        provided.
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

    if not nblocks:
        nblocks = min(floor(sqrt(n)), 100)
    blocksize = n // nblocks

    check_recommendation(
        {
            "nblocks ≤ 100": nblocks <= 100,
            "blocksize > 0.01 * n": blocksize > 0.01 * n,
            "nblocks ≡ ⌊n / blocksize⌋ ": nblocks == n // blocksize,
        }
    )

    if template is None:
        template = make_template(series, blocksize)
    template_size = len(template)

    matches_expect = (blocksize - template_size + 1) / 2 ** template_size
    variance = blocksize * (
        (1 / 2 ** template_size) - ((2 * template_size - 1)) / 2 ** (2 * template_size)
    )

    block_matches = []
    for block_tup in rawblocks(series, blocksize=blocksize):
        matches = 0
        pointer = 0

        boundary = blocksize - template_size
        while pointer < boundary:
            window = block_tup[pointer : pointer + template_size]

            if all(x == y for x, y in zip(window, template)):
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
    template: List
    matches_expect: float
    variance: float
    block_matches: List[int]
    match_diffs: List[float]

    def __str__(self):
        f_stats = self.stats_table("chi-square")

        f_template = self.template
        f_matches_expect = round(self.matches_expect, 1)

        matches_count = Counter(self.block_matches)

        table = sorted(matches_count.items())
        f_table = tabulate(table, headers=["matches", "nblocks"])

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


@stattest(rec_input=288)  # TODO appropiate min input
def overlapping_template_matching(series, template: List = None, nblocks=None, df=5):
    """Overlapping matches of template per block is compared to expected result

    The sequence is split into blocks, where the number of overlapping matches
    to the template in each block is found. This is referenced to the expected
    mean and variance in matches of a hypothetically truly random RNG.

    Parameters
    ----------
    sequence : array-like
        Output of the RNG being tested
    template : Tuple, optional
        Template to match with the sequence, randomly generated if not
        provided.
    nblocks : int
        Number of blocks to split sequence into
    df : int, default `5`
        Degrees of freedom to use in p-value calculation

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

    if not nblocks:
        nblocks = floor(sqrt(n))
    blocksize = n // nblocks

    if not template:
        template = make_template(series, blocksize)
    template_size = len(template)

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

    check_recommendation(
        {
            "n ≥ nblocks * blocksize": n >= nblocks * blocksize,
            "nblocks * min(probabilities) > df": nblocks * min(probabilities) > df,
            "λ ≈ 2": isclose(lambda_, 2),
            "len(template) ≈ log2(nblocks)": isclose(template_size, log2(nblocks)),
            "df ≈ λ": isclose(template_size, log2(nblocks)),
        }
    )

    block_matches = []
    for block_tup in rawblocks(series, blocksize=blocksize):
        matches = 0

        boundary = blocksize - template_size
        for pointer in range(boundary + 1):
            window = block_tup[pointer : pointer + template_size]

            if all(x == y for x, y in zip(window, template)):
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

    p = gammaincc(df / 2, statistic / 2)  # TODO should first param be df / 2

    return OverlappingTemplateMatchingTestResult(
        statistic=statistic,
        p=p,
        template=template,
        expected_tallies=expected_tallies,
        tallies=tallies,
    )


@dataclass
class OverlappingTemplateMatchingTestResult(TestResult):
    template: List
    expected_tallies: List[int]
    tallies: List[int]

    def __post_init__(self):
        self.tally_diffs = []
        for expect, actual in zip(self.expected_tallies, self.tallies):
            diff = actual - expect
            self.tally_diffs.append(diff)

    def __str__(self):
        f_stats = self.stats_table("chi-square")

        f_template = self.template

        f_matches = [f"{x}" for x in range(matches_ceil + 1)]
        f_matches[-1] = f"{f_matches[-1]}+"

        f_expected_tallies = [round(tally, 1) for tally in self.expected_tallies]
        f_diffs = [round(diff, 1) for diff in self.tally_diffs]

        f_table = tabulate(
            zip(f_matches, self.tallies, f_expected_tallies, f_diffs),
            headers=["matches", "count", "expected", "diff"],
        )

        return f"{f_stats}\n" "\n" f"template: {f_template}\n" "\n" f"{f_table}"
