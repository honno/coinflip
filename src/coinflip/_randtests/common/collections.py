from bisect import bisect_left
from collections import defaultdict
from collections.abc import MutableSequence
from functools import lru_cache
from numbers import Real
from typing import Any
from typing import Iterable
from typing import Tuple
from typing import Union

__all__ = ["Bins", "defaultlist", "FloorDict"]


class Bins(dict):
    """Subclassed ``dict`` to initialise intervals as empty bins

    If a key is accessed that does not exist, the nearest interval is used.

    Parameters
    ----------
    intervals: ``Iterable[Real]``
        Indexes to be used to group subsequent

    Examples
    --------
    >>> bins = Bins([0, 1, 2, 3, 4])
    >>> bins
    {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    >>> bins[5] += 10
    >>> bins[4]
    10
    """

    def __init__(self, intervals: Iterable[Real]):
        empty_bins = {interval: 0 for interval in sorted(intervals)}
        super().__init__(empty_bins)

    @property
    def intervals(self) -> Tuple[Real]:
        """The (sorted) intervals of the dict"""
        return tuple(self.keys())

    def __setitem__(self, key: Real, value: Real):
        realkey = self._roundkey(key)
        super().__setitem__(realkey, value)

    def __getitem__(self, key: Real):
        realkey = self._roundkey(key)
        return super().__getitem__(realkey)

    def _roundkey(self, key: Real):
        return Bins._find_closest_interval(self.intervals, key)

    @classmethod
    @lru_cache()
    def _find_closest_interval(cls, intervals: Tuple[Real], key: Real):
        minkey = intervals[0]
        midkeys = intervals[1:-1]
        maxkey = intervals[-1]

        if key <= minkey:
            return minkey
        elif key >= maxkey:
            return maxkey
        elif key in midkeys:
            return key
        else:
            i = bisect_left(intervals, key)
            leftkey = intervals[i - 1]
            rightkey = intervals[i]

            if leftkey - key > rightkey - key:
                return leftkey
            else:
                return rightkey

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, state):
        self.update(state)

    def __reduce__(self):
        return (Bins, (self.intervals,), self.__getstate__())


class defaultlist(MutableSequence):
    """A list with default values

    .. warning:: ``defaultlist`` has not been tested for production use yet
    """

    def __init__(self, default_factory):
        self._defaultdict = defaultdict(default_factory)

    def __getitem__(self, key: Union[int, slice]):
        if isinstance(key, int):
            return self._defaultdict[key]

        elif isinstance(key, slice):
            indices = range(key.start or 1, key.stop, key.step or 1)
            return [self[i] for i in indices]

    def __setitem__(self, key: Union[int, slice], value):
        if isinstance(key, int):
            self._defaultdict[key] = value

        elif isinstance(key, slice):
            raise NotImplementedError()  # TODO

    def __delitem__(self, i: int):
        del self._defaultdict[i]

    def __len__(self):
        indices = self._defaultdict.keys()
        return max(indices) + 1

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __repr__(self):
        f_dict = repr(self._defaultdict)
        return f"defaultlist({f_dict})"

    def insert(self, key: Union[int, slice], value: Any):
        if key < len(self):
            indices = self._defaultdict.keys()
            larger_indexes = [i for i in indices if i >= key]
            reindexed_subdict = {i + 1: self._defaultdict[i] for i in larger_indexes}
            for i in larger_indexes:
                del self._defaultdict[i]
            self._defaultdict.update(reindexed_subdict)

        self._defaultdict[key] = value

    def append(self, value: Any):
        self.insert(len(self), value)


class FloorDict(dict):
    """Subclassed ``dict`` where invalid keys floor to the smallest real key

    If a key is accessed that does not exist, the nearest real key that is the
    less-than of the passed key is used.

    .. warning:: ``FloorDict`` has not been tested for production use yet
    """

    def __missing__(self, key):
        prevkey = None
        for realkey, value in self.items():
            if key < realkey:
                if prevkey is None:
                    raise KeyError("Passed key smaller than all real keys")
                return super().__getitem__(prevkey)
            prevkey = realkey
        else:
            return super().__getitem__(prevkey)
