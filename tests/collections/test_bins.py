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
    def init_bins(self, intervals):
        self.bins = Bins(intervals)

    @rule(i=real(), n=real(allow_infinity=False))
    def increment(self, i, n):
        value_expect = self.bins[i] + n
        self.bins[i] += n
        assert self.bins[i] == value_expect

    @rule()
    def pickle(self):
        pickled_bins = pickle.dumps(self.bins)
        assert pickle.loads(pickled_bins) == self.bins


TestBinsStateMachine = BinsStateMachine.TestCase


def test_duplicate_intervals():
    with raises(ValueError):
        Bins([0, 1, 2, 2, 3])


def test_bisect_step():
    bins = Bins([-6, -3, 0, 3, 6])
    bins[0.5] += 1
    assert bins[3] == 0
    assert bins[0] == 1


def test_del():
    bins = Bins([-6, -3, 0, 3, 6])
    bins[6] += 100
    del bins[6]
    assert bins[3] == 100
