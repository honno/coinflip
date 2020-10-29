from collections import Counter
from dataclasses import dataclass
from math import erfc
from math import sqrt

import pandas as pd
from rich.text import Text
from scipy.stats import chisquare

from coinflip._randtests.common.collections import Bins
from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import MultiTestResult
from coinflip._randtests.common.result import SubTestResult
from coinflip._randtests.common.typing import Integer

__all__ = ["random_excursions", "random_excursions_variant"]

# ------------------------------------------------------------------------------
# Random Excursions Test

# TODO comment why these states and df were chosen
states = [-4, -3, -2, -1, 1, 2, 3, 4]
df = 5

# TODO calculate these dynamically
state_probabilities = {
    1: [0.5000, 0.2500, 0.1250, 0.0625, 0.0312, 0.0312],
    2: [0.7500, 0.0625, 0.0469, 0.0352, 0.0264, 0.0791],
    3: [0.8333, 0.0278, 0.0231, 0.0193, 0.0161, 0.0804],
    4: [0.8750, 0.0156, 0.0137, 0.0120, 0.0105, 0.0733],
    5: [0.9000, 0.0100, 0.0090, 0.0081, 0.0073, 0.0656],
    6: [0.9167, 0.0069, 0.0064, 0.0058, 0.0053, 0.0588],
    7: [0.9286, 0.0051, 0.0047, 0.0044, 0.0041, 0.0531],
}


@randtest()
def random_excursions(series, heads, tails, ctx):
    n = len(series)

    set_task_total(ctx, 4)

    failures = check_recommendations(ctx, {"n ≥ 1000000": n >= 1000000})

    oscillations = series.map({heads: 1, tails: -1})
    cumulative_sums = oscillations.cumsum()

    advance_task(ctx)

    head = pd.Series({-1: 0})
    tail = pd.Series({n + 1: 0})
    walk = pd.concat([head, cumulative_sums, tail])

    advance_task(ctx)

    # TODO standardise or differentiate language of "bins"/"occurences"/"bincounts"
    ncycles = 0
    state_count_bins = {state: Bins(range(df + 1)) for state in states}
    for cycle in ascycles(walk):
        ncycles += 1
        state_counts = Counter(cycle)
        for state in states:
            count = state_counts[state]
            state_count_bins[state][count] += 1

    advance_task(ctx)

    results = {}
    for state in states:
        probabilities = state_probabilities[abs(state)]
        expected_bincounts = [ncycles * prob for prob in probabilities]

        bincounts = state_count_bins[state].values()

        chi2, p = chisquare(list(bincounts), expected_bincounts)

        results[state] = RandomExcursionsSubTestResult(chi2, p, state)

    advance_task(ctx)

    return RandomExcursionsMultiTestResult(heads, tails, failures, results)


@dataclass
class RandomExcursionsSubTestResult(SubTestResult):
    state: Integer


class RandomExcursionsMultiTestResult(MultiTestResult):
    def _pretty_feature(self, result: RandomExcursionsSubTestResult):
        return Text(str(result.state), style="bold")

    def _render(self):
        yield self._results_table("state", "χ²")

    def _render_sub(self, result: RandomExcursionsSubTestResult):
        yield result._pretty_result("chi-square")


def ascycles(walk):
    items = walk.items()
    _, firstval = next(items)
    cycle = [firstval]
    for _, cusum in items:
        if cusum == 0:
            cycle.append(cusum)
            yield cycle
            cycle = [cusum]
        else:
            cycle.append(cusum)


# ------------------------------------------------------------------------------
# Random Excursions Variant Test

variant_states = [-9, -8, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9]


@randtest()
def random_excursions_variant(series, heads, tails, ctx):
    n = len(series)

    set_task_total(ctx, 4)

    failures = check_recommendations(ctx, {"n ≥ 1000000": n >= 1000000})

    oscillations = series.map({heads: 1, tails: -1})
    cumulative_sums = oscillations.cumsum()

    advance_task(ctx)

    head = pd.Series({-1: 0})
    tail = pd.Series({n + 1: 0})
    walk = pd.concat([head, cumulative_sums, tail])

    advance_task(ctx)

    state_counts = walk.value_counts()
    ncycles = state_counts.at[0] - 1

    advance_task(ctx)

    results = {}
    for state in variant_states:
        try:
            count = state_counts.at[state]
        except KeyError:
            count = 0

        p = erfc(abs(count - ncycles) / sqrt(2 * ncycles * (4 * abs(state) - 2)))

        advance_task(ctx)

        results[state] = RandomExcursionsVariantSubTestResult(count, p, state)

    advance_task(ctx)

    return RandomExcursionsVariantMultiTestResult(heads, tails, failures, results)


@dataclass
class RandomExcursionsVariantSubTestResult(SubTestResult):
    state: Integer


class RandomExcursionsVariantMultiTestResult(MultiTestResult):
    def _pretty_feature(self, result: RandomExcursionsVariantSubTestResult):
        return Text(str(result.state), style="bold")

    def _render(self):
        yield self._results_table("state", "ξ")

    def _render_sub(self, result: RandomExcursionsVariantSubTestResult):
        yield result._pretty_result("count")
