from hypothesis import assume
from hypothesis import reject
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import initialize
from hypothesis.stateful import rule

from coinflip.collections import defaultlist

ints = st.lists(st.integers())
chars = st.from_regex(r"[a-z]*", fullmatch=True)


# TODO test extended slices (ugh)
class DefaultListStateMachine(RuleBasedStateMachine):
    @initialize(ints=ints)
    def init_lists(self, ints):
        self.list_ = ints

        self.dlist = defaultlist()
        self.dlist[:] = ints

    @property
    def n(self):
        return len(self.list_)

    @rule(data=st.data())
    def get(self, data):
        assume(self.n > 0)
        i = data.draw(st.integers(min_value=0, max_value=self.n - 1))

        assert self.dlist[i] == self.list_[i]

    @rule(data=st.data(), chars=chars)
    def set(self, data, chars):
        assume(self.n > 0)
        i = data.draw(st.integers(min_value=0, max_value=self.n - 1))

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
        slice_ = data.draw(st.slices(self.n))

        assert self.dlist[slice_] == self.list_[slice_]

    @rule(data=st.data(), chars_or_ints=st.one_of(chars, ints))
    def slice_set(self, data, chars_or_ints):
        slice_ = data.draw(st.slices(self.n))

        try:
            self.list_[slice_] = chars_or_ints
        except ValueError:
            reject()
        self.dlist[slice_] = chars_or_ints

        assert self.dlist == self.list_


TestDefaultListStateMachine = DefaultListStateMachine.TestCase


def test_repr():
    dlist = defaultlist(int)
    dlist.append(42)
    assert repr(dlist) == "[42]"


# def test_slice_defaulting():
#     dlist = defaultlist(int)
#     assert dlist[:2] == [0, 0]
