from collections import Counter
from dataclasses import dataclass
from math import erfc
from math import sqrt
from typing import Dict
from typing import Tuple

import pandas as pd
from scipy.special import gammaincc

from coinflip.randtests._collections import Bins
from coinflip.randtests._decorators import elected
from coinflip.randtests._decorators import randtest
from coinflip.randtests._result import MultiTestResult

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
@elected
def random_excursions(series, candidate):
    n = len(series)

    peak = candidate
    trough = next(value for value in series.unique() if value != candidate)

    oscillations = series.map({peak: 1, trough: -1})

    cumulative_sums = oscillations.cumsum()

    head = pd.Series({-1: 0})
    tail = pd.Series({n + 1: 0})
    walk = pd.concat([head, cumulative_sums, tail])

    # TODO standardise or differentiate language of "bins"/"occurences"/"bincounts"
    ncycles = 0
    state_bins = {state: Bins(range(df + 1)) for state in states}
    for cycle in ascycles(walk):
        ncycles += 1
        state_counts = Counter(cycle)
        for state in states:
            count = state_counts[state]
            state_bins[state][count] += 1

    results = {}
    for state in states:
        bincounts = state_bins[state].values()

        probabilities = state_probabilities[abs(state)]
        expected_bincounts = [ncycles * prob for prob in probabilities]

        reality_check = []
        for count_expect, count in zip(expected_bincounts, bincounts):
            diff = (count - count_expect) ** 2 / count_expect
            reality_check.append(diff)

        statistic = sum(reality_check)
        p = gammaincc(df / 2, statistic / 2)

        results[state] = (statistic, p)

    return RandomExcursionsTestResult(results)


@dataclass
class RandomExcursionsTestResult(MultiTestResult):
    results: Dict[int, Tuple[float, float]]

    @property
    def statistics(self):
        return [statistic for statistic, _ in self.results.values()]

    @property
    def pvalues(self):
        return [p for _, p in self.results.values()]


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
@elected
def random_excursions_variant(series, candidate):
    n = len(series)

    peak = candidate
    trough = next(value for value in series.unique() if value != candidate)

    oscillations = series.map({peak: 1, trough: -1})

    cumulative_sums = oscillations.cumsum()

    head = pd.Series({-1: 0})
    tail = pd.Series({n + 1: 0})
    walk = pd.concat([head, cumulative_sums, tail])

    state_counts = walk.value_counts()
    ncycles = state_counts.at[0] - 1

    results = {}
    for state in variant_states:
        try:
            count = state_counts.at[state]
        except IndexError:
            count = 0

        p = erfc(abs(count - ncycles) / sqrt(2 * ncycles * (4 * abs(state) - 2)))

        results[state] = (count, p)

    print(results)

    return RandomExcursionsTestResult(results)
