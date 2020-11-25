from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import initialize
from hypothesis.stateful import rule

from coinflip.collections import defaultlist

chars = st.from_regex(r"[a-z]")


# TODO test extended slices (ugh)
def slices(n):
    return st.slices(n).filter(lambda k: k.step is None or k.step == 1)


class DefaultListStateMachine(RuleBasedStateMachine):
    @initialize(ints=st.lists(st.integers()))
    def init_lists(self, ints):
        self.list_ = ints

        self.dlist = defaultlist()
        self.dlist[:] = ints

    @rule(data=st.data())
    def slice_get(self, data):
        slice_ = data.draw(slices(len(self.list_)))
        self.dlist[slice_] == self.list_[slice_]

    @rule(data=st.data(), chars=st.one_of(chars, st.lists(chars)))
    def slice_set(self, data, chars):
        slice_ = data.draw(slices(len(self.list_)))

        self.list_[slice_] = chars
        self.dlist[slice_] = chars

        assert self.dlist == self.list_


TestDefaultListStateMachine = DefaultListStateMachine.TestCase


def test_set_slice():
    dlist = defaultlist(int)
    dlist[:] = [0, 1, 2, 3, 4]

    dlist[:1] = ["a", "b", "c"]

    assert dlist == ["a", "b", "c", 1, 2, 3, 4]


def test_repr():
    dlist = defaultlist(int)
    dlist.append(42)
    assert repr(dlist) == "[42]"
