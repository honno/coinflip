from defaultlist import defaultlist as ref_defaultlist
from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine
from hypothesis.stateful import initialize
from hypothesis.stateful import rule
from pytest import fixture

from coinflip.collections import defaultlist

ints = st.lists(st.integers())
chars = st.from_regex(r"[a-z]*", fullmatch=True)


# we disagree about slices so we use no rules for slice accessors
class DefaultListStateMachine(RuleBasedStateMachine):
    @initialize(ints=ints)
    def init_lists(self, ints):
        self.ref_dlist = ref_defaultlist()
        self.dlist = defaultlist()

        assert self.dlist == self.ref_dlist

    @property
    def n(self):
        return len(self.ref_dlist)

    @rule(chars=chars)
    def append(self, chars):
        self.ref_dlist.append(chars)
        self.dlist.append(chars)

        assert self.dlist == self.ref_dlist

    @rule(ints=ints)
    def concat(self, ints):
        self.ref_dlist += ints
        self.dlist += ints

        assert self.dlist == self.ref_dlist

    @rule(data=st.data())
    def get(self, data):
        assume(self.n > 0)
        i = data.draw(st.integers(min_value=0, max_value=self.n - 1))

        assert self.dlist[i] == self.ref_dlist[i]

    @rule(data=st.data(), chars=chars)
    def set(self, data, chars):
        assume(self.n > 0)
        i = data.draw(st.integers(min_value=0, max_value=self.n - 1))

        self.ref_dlist[i] = chars
        self.dlist[i] = chars

        assert self.dlist == self.ref_dlist

    @rule(data=st.data())
    def del_(self, data):
        assume(self.n > 0)
        i = data.draw(st.integers(min_value=0, max_value=self.n - 1))

        del self.ref_dlist[i]
        del self.dlist[i]

        assert self.dlist == self.ref_dlist


TestDefaultListStateMachine = DefaultListStateMachine.TestCase


@fixture
def dlist():
    return defaultlist()


def test_repr(dlist):
    dlist.append(42)
    assert repr(dlist) == "[42]"


def test_slice_del(dlist):
    dlist[:] = range(15)
    dlist[20] = 20

    del dlist[0:10:2]

    assert dlist == [
        1,
        3,
        5,
        7,
        9,
        10,
        11,
        12,
        13,
        14,
        None,
        None,
        None,
        None,
        None,
        20,
    ]
