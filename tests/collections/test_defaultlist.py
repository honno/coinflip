from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import initialize
from hypothesis.stateful import rule

from coinflip.collections import defaultlist

ints = st.lists(st.integers())
chars = st.from_regex(r"[a-z]*", fullmatch=True)


# TODO test extended slices (ugh)
def slices(n):
    return st.slices(n).filter(lambda k: k.step is None or k.step == 1)


class DefaultListStateMachine(RuleBasedStateMachine):
    @initialize(ints=ints)
    def init_lists(self, ints):
        self.list_ = ints

        self.dlist = defaultlist()
        self.dlist[:] = ints

    @rule(data=st.data())
    def get(self, data):
        n = len(self.list_)
        assume(n > 0)
        i = data.draw(st.integers(min_value=0, max_value=n - 1))

        assert self.dlist[i] == self.list_[i]

    @rule(data=st.data(), chars=chars)
    def set(self, data, chars):
        n = len(self.list_)
        assume(n > 0)
        i = data.draw(st.integers(min_value=0, max_value=n - 1))

        self.list_[i] = chars
        self.dlist[i] = chars

        assert self.dlist == self.list_

    @rule(chars=chars)
    def append(self, chars):
        self.list_.append(chars)
        self.dlist.append(chars)

        assert self.dlist == self.list_

    @rule(ints=ints)
    def concat(self, ints):
        self.list_ += ints
        self.dlist += ints

        assert self.dlist == self.list_

    @rule(data=st.data())
    def slice_get(self, data):
        slice_ = data.draw(slices(len(self.list_)))
        self.dlist[slice_] == self.list_[slice_]

    @rule(data=st.data(), chars_or_ints=st.one_of(chars, ints))
    def slice_set(self, data, chars_or_ints):
        slice_ = data.draw(slices(len(self.list_)))

        self.list_[slice_] = chars_or_ints
        self.dlist[slice_] = chars_or_ints

        assert self.dlist == self.list_


TestDefaultListStateMachine = DefaultListStateMachine.TestCase


def test_repr():
    dlist = defaultlist(int)
    dlist.append(42)
    assert repr(dlist) == "[42]"
