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

import altair as alt
import pandas as pd
from rich.text import Text
from scipy.special import gammaincc
from scipy.special import hyp1f1
from scipy.stats import chisquare

from coinflip._randtests.common.collections import defaultlist
from coinflip._randtests.common.core import *
from coinflip._randtests.common.pprint import pretty_subseq
from coinflip._randtests.common.result import MultiTestResult
from coinflip._randtests.common.result import SubTestResult
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.result import make_chisquare_table
from coinflip._randtests.common.result import make_testvars_table
from coinflip._randtests.common.result import plot_chi2_dist
from coinflip._randtests.common.testutils import blocks
from coinflip._randtests.common.testutils import rawblocks
from coinflip._randtests.common.testutils import slider
from coinflip._randtests.common.typing import Face
from coinflip._randtests.common.typing import Float
from coinflip._randtests.common.typing import Integer

__all__ = ["non_overlapping_template_matching", "overlapping_template_matching"]


# ------------------------------------------------------------------------------
# Non-overlapping Template Matching Test


@randtest()
def non_overlapping_template_matching(
    series,
    heads,
    tails,
    ctx,
    template_size=None,
    blocksize=None,
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

    failures = check_recommendations(
        ctx,
        {
            "n ≥ 100": n >= 100,
            "template_size = 9 or 10": template_size == 9 or template_size == 10,
            "blocksize > 0.01 * n": blocksize > 0.01 * n,
            "nblocks ≤ 100": nblocks <= 100,  # TODO same thing as above?
            "nblocks = ⌊n / blocksize⌋": nblocks == n // blocksize,
        },
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

        statistic = sum(diff ** 2 / variance for diff in match_diffs)
        p = gammaincc(nblocks / 2, statistic / 2)

        results[template] = NonOverlappingTemplateMatchingSubTestResult(
            statistic,
            p,
            template,
            block_matches,
            match_diffs,
        )

    advance_task(ctx)

    return NonOverlappingTemplateMatchingMultiTestResult(
        heads,
        tails,
        failures,
        results,
        template_size,
        blocksize,
        nblocks,
        matches_expect,
        variance,
    )


@dataclass(unsafe_hash=True)
class NonOverlappingTemplateMatchingSubTestResult(SubTestResult):
    template: Tuple[Face, ...]
    block_matches: List[Integer]
    match_diffs: List[Float]


@dataclass(unsafe_hash=True)
class NonOverlappingTemplateMatchingMultiTestResult(MultiTestResult):
    template_size: Integer
    blocksize: Integer
    nblocks: Integer
    matches_expect: Float
    variance: Float

    def _pretty_feature(self, result: NonOverlappingTemplateMatchingSubTestResult):
        f_template = pretty_subseq(result.template, self.heads, self.tails)

        return f_template

    # TODO q value
    def _render(self):
        yield self._pretty_inputs(
            ("blocksize", self.blocksize),
            ("nblocks", self.nblocks),
        )

        yield self._results_table("template", "χ²")

    def _render_sub(self, result: NonOverlappingTemplateMatchingSubTestResult):
        yield result._pretty_result("chi-square")

        title = Text("matches of ")
        title.append(pretty_subseq(result.template, self.heads, self.tails))
        title.append(" per block")

        f_matches_expect = round(self.matches_expect, 1)
        caption = f"expected {f_matches_expect} matches"

        matches_count = Counter(result.block_matches)
        table = sorted(matches_count.items())
        f_table = make_testvars_table(
            "matches", "nblocks", title=title, caption=caption
        )
        for matches, nblocks in table:
            f_table.add_row(str(matches), str(nblocks))

        yield f_table


# ------------------------------------------------------------------------------
# Overlapping Template Matching Test


# TODO Review paper "Correction of OTM Test Included in the NIST Randomness Test Suite"
@randtest()  # TODO appropiate min input
def overlapping_template_matching(
    series,
    heads,
    tails,
    ctx,
    template_size=None,
    blocksize=None,
    matches_ceil=None,
):
    n = len(series)

    if matches_ceil is None:
        matches_ceil = 5
    df = matches_ceil  # there are matches_ceil + 1 independent scores

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

    expected_tallies = [prob * nblocks for prob in probabilities]

    failures = check_recommendations(
        ctx,
        {
            "n ≥ 288": n >= 288,
            "n ≥ nblocks * blocksize": n >= nblocks * blocksize,
            "min(expected_tallies) > df": min(expected_tallies) > df,
            "λ ≈ 2": isclose(lambda_, 2),
            "len(template) ≈ log2(nblocks)": isclose(template_size, log2(nblocks)),
            "df ≈ 2 * λ": isclose(template_size, 2 * lambda_),
        },
    )

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
        i = min(matches, matches_ceil)
        tallies[i] += 1

    advance_task(ctx)

    statistic, p = chisquare(tallies, expected_tallies)

    advance_task(ctx)

    return OverlappingTemplateMatchingTestResult(
        heads,
        tails,
        failures,
        statistic,
        p,
        template_size,
        blocksize,
        matches_ceil,
        nblocks,
        lambda_,
        template,
        expected_tallies,
        tallies,
    )


@dataclass
class OverlappingTemplateMatchingTestResult(TestResult):
    template_size: Integer
    blocksize: Integer
    matches_ceil: Integer
    nblocks: Integer
    lambda_: Float
    template: Tuple[Face, ...]
    expected_tallies: List[Integer]
    tallies: List[Integer]

    def _fmt_matches(self):
        f_matches = [str(x) for x in range(self.matches_ceil + 1)]
        f_matches[-1] = f"{f_matches[-1]}+"

        return f_matches

    def _render(self):
        yield self._pretty_result("chi-square")

        yield TestResult._pretty_inputs(
            ("template size", self.template_size),
            ("blocksize", self.blocksize),
            ("nblocks", self.nblocks),
        )

        title = Text("matches of ")
        title.append(pretty_subseq(self.template, self.heads, self.tails))
        title.append(" per block")

        f_matches = self._fmt_matches()

        table = make_chisquare_table(
            title,
            "matches",
            f_matches,
            self.expected_tallies,
            self.tallies,
        )

        yield table

    def plot_template_matches(self):
        df = pd.DataFrame(
            {
                "matches": self._fmt_matches(),
                "expected": self.expected_tallies,
                "observed": self.tallies,
            }
        )
        df = df.melt("matches", var_name="type", value_name="nblocks")

        f_template = pretty_subseq(self.template, self.heads, self.tails)

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                alt.X("matches", title="Matches"),
                alt.Y(
                    "nblocks:Q",
                    title="Number of blocks",
                ),
                column=alt.Column(
                    "type:N",
                    title=None,
                ),
            )
            .properties(title=f"Overlapping matches of {f_template} per block")
        )

        return chart

    def plot_refdist(self):
        return plot_chi2_dist(self.statistic, self.matches_ceil)
