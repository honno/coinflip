from math import ceil
from numbers import Real
from typing import List

from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import initialize
from hypothesis.stateful import rule
from hypothesis.strategies import SearchStrategy

from coinflip.collections import Bins


def real(min_value: Real = None) -> SearchStrategy[Real]:
    return st.one_of(
        st.integers(min_value=ceil(min_value) if min_value else None),
        st.floats(
            min_value=float(min_value) if min_value else None,
            allow_nan=False,
            allow_infinity=False,
        ),
    )


@st.composite
def intervals(draw) -> SearchStrategy[List[Real]]:
    n = draw(st.integers(min_value=2))

    x = draw(real())
    intervals = [x]
    for _ in range(n - 1):
        x = draw(real(min_value=x + 1))
        intervals.append(x)

    return intervals


class BinsStateMachine(RuleBasedStateMachine):
    @initialize(intervals=intervals())
    def init_bin(self, intervals):
        self.bins = Bins(intervals)

    @rule(i=real(), n=real())
    def increment(self, i, n):
        value_expect = self.bins[i] + n
        self.bins[i] += n
        assert self.bins[i] == value_expect


TestBinsStateMachine = BinsStateMachine.TestCase
