import pickle
from numbers import Real
from typing import List

from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import initialize
from hypothesis.stateful import rule
from hypothesis.strategies import SearchStrategy
from pytest import raises

from coinflip.collections import Bins

from ..strategies import real


@st.composite
def intervals(draw) -> SearchStrategy[List[Real]]:
    n = draw(st.integers(min_value=2))

    x = draw(real())
    intervals = [x]
    for _ in range(n - 1):
        x = draw(real().filter(lambda x: x not in intervals))
        intervals.append(x)

    return intervals


class BinsStateMachine(RuleBasedStateMachine):
    @initialize(intervals=intervals())
    def init_bin(self, intervals):
        self.bins = Bins(intervals)
        print(intervals)
        print(self.bins)

    @rule(i=real(), n=real(allow_infinity=False))
    def increment(self, i, n):
        value_expect = self.bins[i] + n
        self.bins[i] += n
        assert self.bins[i] == value_expect

    @rule()
    def pickle(self):
        pickled_bins = pickle.dumps(self.bins)
        assert self.bins == pickle.loads(pickled_bins)


TestBinsStateMachine = BinsStateMachine.TestCase


def test_duplicate_intervals():
    with raises(ValueError):
        Bins([0, 1, 2, 2, 3])
