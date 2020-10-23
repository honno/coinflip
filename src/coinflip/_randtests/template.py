from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from itertools import product
from math import ceil
from math import exp
from math import floor
from math import isclose
from math import log2
from math import sqrt
from typing import List
from typing import Tuple

from rich.text import Text
from scipy.special import gammaincc
from scipy.special import hyp1f1
from scipy.stats import chisquare

from coinflip import encoders as enc
from coinflip._randtests.common.collections import defaultlist
from coinflip._randtests.common.core import *
from coinflip._randtests.common.pprint import pretty_subseq
from coinflip._randtests.common.result import MultiTestResult
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import encode
from coinflip._randtests.common.result import make_chisquare_table
from coinflip._randtests.common.result import make_testvars_table
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.testutils import rawblocks
from coinflip._randtests.common.testutils import slider
from coinflip.typing import Face

__all__ = ["non_overlapping_template_matching", "overlapping_template_matching"]


@dataclass
class BaseTemplateMatchingTestResult(TestResult):
    template: Tuple[Face, ...] = encode(enc.tuple_(enc.faces))
    template_size: int = encode(enc.int_)
    blocksize: int = encode(enc.int_)
    nblocks: int = encode(enc.int_)

    def pretty_template(self) -> Text:
        return pretty_subseq(self.template, self.heads, self.tails)


# ------------------------------------------------------------------------------
# Non-overlapping Template Matching Test


@randtest()
def non_overlapping_template_matching(
    series, heads, tails, ctx, template_size=None, blocksize=None,
):
    n = len(series)

    if not blocksize:
        blocksize = max(ceil(0.01 * n), 6)
        if blocksize % 2 != 0:
            blocksize -= 1
    nblocks = n // blocksize

    if not template_size:
        template_size = max(min(blocksize // 3, 9), 2)

    nblocks_sub = blocksize // template_size
    set_task_total(ctx, 1 + nblocks * (nblocks_sub + 1) + 1)

    check_recommendations(
        {
            "n ≥ 100": n >= 100,
            "template_size = 9 or 10": template_size == 9 or template_size == 10,
            "blocksize > 0.01 * n": blocksize > 0.01 * n,
            "nblocks ≤ 100": nblocks <= 100,  # TODO same thing as above?
            "nblocks = ⌊n / blocksize⌋": nblocks == n // blocksize,
        }
    )

    matches_expect = (blocksize - template_size + 1) / 2 ** template_size
    variance = blocksize * (
        (1 / 2 ** template_size) - ((2 * template_size - 1)) / 2 ** (2 * template_size)
    )

    advance_task(ctx)

    template_block_matches = defaultdict(lambda: defaultlist(int))
    for i, block in enumerate(blocks(series, blocksize)):
        matches = defaultdict(int)

        for window_tup in rawblocks(block, template_size):
            matches[window_tup] += 1

            advance_task(ctx)

        for template, matches in matches.items():
            template_block_matches[template][i] = matches

        advance_task(ctx)

    results = {}
    for template in product([heads, tails], repeat=template_size):
        block_matches = template_block_matches[template][:nblocks]
        match_diffs = [matches - matches_expect for matches in block_matches]

        statistic = sum(diff ** 2 / variance for diff in block_matches)
        p = gammaincc(nblocks / 2, statistic / 2)

        results[template] = NonOverlappingTemplateMatchingTestResult(
            heads,
            tails,
            statistic,
            p,
            template,
            template_size,
            nblocks,
            blocksize,
            matches_expect,
            variance,
            block_matches,
            match_diffs,
        )

    advance_task(ctx)

    return MultiNonOverlappingTemplateMatchingTestResult(results)


@dataclass(unsafe_hash=True)
class NonOverlappingTemplateMatchingTestResult(BaseTemplateMatchingTestResult):
    matches_expect: float = encode(enc.float_)
    variance: float = encode(enc.float_)
    block_matches: List[int] = encode(enc.list_(enc.int_))
    match_diffs: List[float] = encode(enc.list_(enc.float_))

    def _render(self):
        yield self._pretty_result("chi-square")

        yield TestResult._pretty_inputs(
            ("blocksize", self.blocksize), ("nblocks", self.nblocks),
        )

        title = Text("matches of ")
        title.append(self.pretty_template())
        title.append(" per block")

        f_matches_expect = round(self.matches_expect, 1)
        caption = f"expected {f_matches_expect} matches"

        matches_count = Counter(self.block_matches)
        table = sorted(matches_count.items())
        f_table = make_testvars_table(
            "matches", "nblocks", title=title, caption=caption
        )
        for matches, nblocks in table:
            f_table.add_row(str(matches), str(nblocks))
        yield f_table


class MultiNonOverlappingTemplateMatchingTestResult(MultiTestResult):
    def _pretty_feature(self, result: NonOverlappingTemplateMatchingTestResult):
        f_template = result.pretty_template()
        return f_template

    # TODO q value
    def _render(self):
        yield self._results_table("template", "χ²")


# ------------------------------------------------------------------------------
# Overlapping Template Matching Test


matches_ceil = 5


# TODO Review paper "Correction of Overlapping Template Matching Test Included in
#                    NIST Randomness Test Suite"
@randtest()  # TODO appropiate min input
def overlapping_template_matching(
    series, heads, tails, ctx, template_size=None, blocksize=None, df=5
):
    n = len(series)

    if not blocksize:
        blocksize = floor(sqrt(n))
    nblocks = n // blocksize

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

    set_task_total(ctx, 1 + nblocks + 2)

    check_recommendations(
        {
            "n ≥ 288": n >= 288,
            "n ≥ nblocks * blocksize": n >= nblocks * blocksize,
            "nblocks * min(probabilities) > df": nblocks * min(probabilities) > df,
            "λ ≈ 2": isclose(lambda_, 2),
            "len(template) ≈ log2(nblocks)": isclose(template_size, log2(nblocks)),
            "df ≈ 2 * λ": isclose(template_size, 2 * lambda_),
        }
    )

    expected_tallies = [prob * nblocks for prob in probabilities]

    advance_task(ctx)

    block_matches = []
    for block in blocks(series, blocksize):
        matches = 0

        for window_tup in slider(block, template_size):
            if all(x == y for x, y in zip(window_tup, template)):
                matches += 1

        advance_task(ctx)

        block_matches.append(matches)

    tallies = [0 for _ in range(matches_ceil + 1)]
    for matches in block_matches:
        i = min(matches, 5)
        tallies[i] += 1

    advance_task(ctx)

    statistic, p = chisquare(tallies, expected_tallies)

    advance_task(ctx)

    return OverlappingTemplateMatchingTestResult(
        heads,
        tails,
        statistic,
        p,
        template,
        template_size,
        blocksize,
        nblocks,
        expected_tallies,
        tallies,
    )


@dataclass
class OverlappingTemplateMatchingTestResult(BaseTemplateMatchingTestResult):
    expected_tallies: List[int] = encode(enc.list_(enc.int_))
    tallies: List[int] = encode(enc.list_(enc.int_))

    def _render(self):
        yield self._pretty_result("chi-square")

        yield TestResult._pretty_inputs(
            ("template size", self.template_size),
            ("blocksize", self.blocksize),
            ("nblocks", self.nblocks),
        )

        title = Text("matches of ")
        title.append(self.pretty_template())
        title.append(" per block")

        f_nmatches = [f"{x}" for x in range(matches_ceil + 1)]
        f_nmatches[-1] = f"{f_nmatches[-1]}+"

        table = make_chisquare_table(
            title, "matches", f_nmatches, self.expected_tallies, self.tallies,
        )

        yield table
