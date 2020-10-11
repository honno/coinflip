from collections import Counter
from dataclasses import dataclass
from itertools import product
from math import exp
from math import floor
from math import isclose
from math import log2
from math import sqrt
from typing import Any
from typing import List
from typing import Tuple

from rich.text import Text
from scipy.special import gammaincc
from scipy.special import hyp1f1

from coinflip._randtests.common.pprint import pretty_subseq
from coinflip._randtests.common.result import MultiTestResult
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_testvars_table
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.testutils import check_recommendations
from coinflip._randtests.common.testutils import randtest
from coinflip._randtests.common.testutils import slider

__all__ = ["non_overlapping_template_matching", "overlapping_template_matching"]


@dataclass
class BaseTemplateMatchingTestResult(TestResult):
    template: Tuple[Any, ...]
    template_size: int
    nblocks: int

    def pretty_template(self) -> Text:
        return pretty_subseq(self.template, self.heads, self.tails)


# ------------------------------------------------------------------------------
# Non-overlapping Template Matching Test


@randtest()
def non_overlapping_template_matching(
    series, heads, tails, template_size=None, nblocks=None
):
    n = len(series)

    if not nblocks:
        nblocks = min(floor(sqrt(n)), 100)
    blocksize = n // nblocks

    if not template_size:
        template_size = min(max(floor(sqrt(blocksize)), 2), 12)

    check_recommendations(
        {
            "n ≥ 288": n
            >= 288,  # template_size=9, nblocks=8, blocksize=4*template_size
            "nblocks ≤ 100": nblocks <= 100,
            "blocksize > 0.01 * n": blocksize > 0.01 * n,
            "nblocks ≡ ⌊n / blocksize⌋": nblocks == n // blocksize,
        }
    )

    tails = next(value for value in series.unique() if value != heads)

    results = {}
    for template in product([heads, tails], repeat=template_size):
        matches_expect = (blocksize - template_size + 1) / 2 ** template_size
        variance = blocksize * (
            (1 / 2 ** template_size)
            - ((2 * template_size - 1)) / 2 ** (2 * template_size)
        )

        block_matches = []
        for block in blocks(series, blocksize):
            matches = 0

            for window_tup in slider(block, template_size):
                if all(x == y for x, y in zip(window_tup, template)):
                    matches += 1

            block_matches.append(matches)

        match_diffs = [matches - matches_expect for matches in block_matches]

        statistic = sum(diff ** 2 / variance for diff in match_diffs)
        p = gammaincc(nblocks / 2, statistic / 2)

        results[template] = NonOverlappingTemplateMatchingTestResult(
            heads,
            tails,
            statistic,
            p,
            template,
            template_size,
            nblocks,
            matches_expect,
            variance,
            block_matches,
            match_diffs,
        )

    return MultiNonOverlappingTemplateMatchingTestResult(results)


@dataclass(unsafe_hash=True)
class NonOverlappingTemplateMatchingTestResult(BaseTemplateMatchingTestResult):
    matches_expect: float
    variance: float
    block_matches: List[int]
    match_diffs: List[float]

    def __rich_console__(self, console, options):
        yield self._results_text("chi-square")

        yield ""

        yield Text("template: ") + self.pretty_template()

        f_matches_expect = round(self.matches_expect, 1)
        yield f"expected matches per block: {f_matches_expect}"

        matches_count = Counter(self.block_matches)
        table = sorted(matches_count.items())
        f_table = make_testvars_table("matches", "nblocks")
        for matches, nblocks in table:
            f_table.add_row(str(matches), str(nblocks))
        yield f_table


class MultiNonOverlappingTemplateMatchingTestResult(MultiTestResult):
    def __rich_console__(self, console, options):
        min_template, min_result = self.min

        f_table = make_testvars_table("template", "statistic", "p-value")
        for template, result in self.items():
            f_template = result.pretty_template()
            if template == min_template:
                f_template.stylize("on blue")

            f_statistic = str(round(result.statistic, 3))
            f_p = str(round(result.p, 3))

            f_table.add_row(f_template, f_statistic, f_p)

        yield f_table

        yield ""

        yield Text("lowest p-value", style="on blue")
        yield min_result


# ------------------------------------------------------------------------------
# Overlapping Template Matching Test


matches_ceil = 5


# TODO Review paper "Correction of Overlapping Template Matching Test Included in
#                    NIST Randomness Test Suite"
@randtest()  # TODO appropiate min input
def overlapping_template_matching(
    series, heads, tails, template_size=None, nblocks=None, df=5
):
    n = len(series)

    if not nblocks:
        nblocks = floor(sqrt(n))
    blocksize = n // nblocks

    if not template_size:
        template_size = min(max(floor(sqrt(blocksize)), 2), 12)
    template = [heads for _ in range(template_size)]

    lambda_ = (blocksize - template_size + 1) / 2 ** template_size
    eta = lambda_ / 2

    first_prob = exp(-eta)
    probabilities = [first_prob]
    for matches in range(1, matches_ceil):
        prob = ((eta * exp(-2 * eta)) / 2 ** matches) * hyp1f1(matches + 1, 2, eta)
        probabilities.append(prob)
    last_prob = 1 - sum(probabilities)
    probabilities.append(last_prob)

    check_recommendations(
        {
            "n ≥ 288": n >= 288,
            "n ≥ nblocks * blocksize": n >= nblocks * blocksize,
            "nblocks * min(probabilities) > df": nblocks * min(probabilities) > df,
            "λ ≈ 2": isclose(lambda_, 2),
            "len(template) ≈ log2(nblocks)": isclose(template_size, log2(nblocks)),
            "df ≈ λ": isclose(template_size, log2(nblocks)),
        }
    )

    expected_tallies = [prob * nblocks for prob in probabilities]

    block_matches = []
    for block in blocks(series, blocksize):
        matches = 0

        for window_tup in slider(block, template_size, overlap=True):
            if all(x == y for x, y in zip(window_tup, template)):
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
        heads,
        tails,
        statistic,
        p,
        template,
        template_size,
        nblocks,
        expected_tallies,
        tallies,
    )


@dataclass
class OverlappingTemplateMatchingTestResult(BaseTemplateMatchingTestResult):
    expected_tallies: List[int]
    tallies: List[int]

    def __post_init__(self):
        self.tally_diffs = []
        for expect, actual in zip(self.expected_tallies, self.tallies):
            diff = actual - expect
            self.tally_diffs.append(diff)

    def __rich_console__(self, console, options):
        yield self._results_text("chi-square")

        yield ""

        yield Text("template: ") + self.pretty_template()

        f_nmatches = [f"{x}" for x in range(matches_ceil + 1)]
        f_nmatches[-1] = f"{f_nmatches[-1]}+"

        table = zip(f_nmatches, self.tallies, self.expected_tallies, self.tally_diffs)
        f_table = make_testvars_table("matches", "count", "expected", "diff")
        for f_matches, count, count_expect, diff in table:
            f_count = str(count)
            f_count_expect = str(round(count_expect, 1))
            f_diff = str(round(diff, 1))
            f_table.add_row(f_matches, f_count, f_count_expect, f_diff)

        yield f_table
