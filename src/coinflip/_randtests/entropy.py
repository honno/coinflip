from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from math import floor
from math import log
from math import log2
from typing import DefaultDict
from typing import Dict
from typing import Tuple

import altair as alt
import pandas as pd
from scipy.special import gammaincc

from coinflip._randtests.common.core import *
from coinflip._randtests.common.result import TestResult
from coinflip._randtests.common.testutils import slider
from coinflip._randtests.common.typing import Face
from coinflip._randtests.common.typing import Float
from coinflip._randtests.common.typing import Integer

__all__ = ["approximate_entropy"]


@randtest()
def approximate_entropy(series, heads, tails, ctx, blocksize=None):
    n = len(series)

    if not blocksize:
        blocksize = max(floor(log2(n)) - 5 - 1, 2)

    set_task_total(ctx, (n + 2) * 2 + 1)

    failures = check_recommendations(
        ctx, {"blocksize < ⌊log2(n)⌋ - 5": blocksize < floor(log2(n)) - 5}
    )

    permutation_counts = {}
    phis = {}
    for template_size in [blocksize, blocksize + 1]:
        head = series[: template_size - 1]
        ouroboros = pd.concat([series, head])

        permcounts = defaultdict(int)
        for window_tup in slider(ouroboros, template_size):
            permcounts[window_tup] += 1

            advance_task(ctx)

        permutation_counts[template_size] = permcounts

        logcounts = defaultdict(int)
        for count in permcounts.values():
            normcount = count / n
            linearithmic_normcount = normcount * log(normcount)
            logcounts[count] += linearithmic_normcount

        advance_task(ctx)

        phi = sum(logcounts.values())
        phis[template_size] = phi

        advance_task(ctx)

    approx_entropy = phis[blocksize] - phis[blocksize + 1]
    chi2 = 2 * n * (log(2) - approx_entropy)
    p = gammaincc(2 ** (blocksize - 1), chi2 / 2)

    advance_task(ctx)

    return ApproximateEntropyTestResult(
        heads,
        tails,
        failures,
        chi2,
        p,
        blocksize,
        permutation_counts,
        phis,
        approx_entropy,
    )


@dataclass
class ApproximateEntropyTestResult(TestResult):
    blocksize: Integer
    permutation_counts: Dict[Integer, DefaultDict[Tuple[Face, ...], Integer]]
    phis: Dict[Integer, Float]
    approx_entropy: Float

    def _render(self):
        yield self._pretty_result("chi-square")

    def plot_permutation_counts(self):
        dfs = []
        for template_size in [self.blocksize, self.blocksize + 1]:
            permcounts = self.permutation_counts[template_size]
            ncounts = Counter(permcounts.values())

            df = pd.DataFrame(
                {
                    "count": ncounts.keys(),
                    "ncounts": ncounts.values(),
                }
            )
            df["blocksize"] = template_size
            dfs.append(df)

        chart = (
            alt.Chart(pd.concat(dfs))
            .mark_bar()
            .encode(
                x=alt.X("count", title="Permutation counts"),
                y=alt.Y("ncounts", title="Number of counts"),
                color="blocksize:O",
            )
            .properties(title="Permutation counts")
        )

        return chart
