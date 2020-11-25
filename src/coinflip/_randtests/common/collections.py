from bisect import bisect_left
from collections import Counter
from collections import OrderedDict
from collections import defaultdict
from collections.abc import MutableMapping
from collections.abc import MutableSequence
from functools import lru_cache
from numbers import Real
from typing import Any
from typing import Callable
from typing import Iterable
from typing import KeysView
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Union

__all__ = ["Bins", "defaultlist", "FloorDict"]


class Bins(MutableMapping):
    """Mapping that initialises intervals as empty bins

    If a key is accessed that does not exist, the nearest interval is used.

    Parameters
    ----------
    intervals : ``Iterable[Real]``
        Non-existent keys will round to the closest of these intervals

    Examples
    --------
    >>> bins = Bins([-6, -3, 0, 3, 6])
    >>> bins
    {-6: 0, -3: 0, 0: 0, 3: 0, 6: 0}
    >>> bins[3] += 1                    # n = 3
    >>> bins
    {-6: 0, -3: 0, 0: 0, 3: 1, 6: 0}
    >>> bins[7] += 1                    # n = 6
    >>> bins[11] += 1                   # n = 6
    >>> bins[6.5] += 1                  # n = 6
    >>> bins
    {-6: 0, -3: 0, 0: 0, 3: 1, 6: 3}
    >>> bins[-1000000] += 1             # n = -6
    >>> bins
    {-6: 1, -3: 0, 0: 0, 3: 1, 6: 3}
    >>> bins[0.5] += 1                  # n = 0
    >>> bins
    {-6: 1, -3: 0, 0: 1, 3: 1, 6: 3}
    >>> del bins[6]
    {-6: 1, -3: 0, 0: 1, 3: 4}
    """

    def __init__(self, intervals: Iterable[Real]):
        counts = Counter(intervals)
        if any(count > 1 for count in counts.values()):
            raise ValueError("Duplicate intervals for binning were passed")

        empty_bins = {interval: 0 for interval in intervals}
        self._odict = OrderedDict(empty_bins)

    @property
    def intervals(self) -> Tuple[Real]:
        return tuple(self._odict.keys())

    def __getitem__(self, key: Real):
        interval = self._roundkey(key)
        return self._odict[interval]

    def __setitem__(self, key: Real, value: Real):
        interval = self._roundkey(key)
        self._odict[interval] = value

    def __delitem__(self, key: Real):
        value = self._odict[key]
        del self._odict[key]
        self[key] += value

    def _roundkey(self, key: Real):
        return find_closest_interval(self.intervals, key)

    def __iter__(self):
        return iter(self._odict)

    def __len__(self):
        return len(self._odict)

    def __repr__(self):
        return str(dict(self))

    def __str__(self):
        return f"Bins({repr(self)})"


@lru_cache()
def find_closest_interval(intervals: Tuple[Real], key: Real):
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

        if abs(leftkey - key) < abs(rightkey - key):
            return leftkey
        else:
            return rightkey


class defaultlist(MutableSequence):
    """A list with default values

    Parameters
    ----------
    default_factory : ``Callable``, optional
    """

    def __init__(self, default_factory: Optional[Callable] = None):
        self._ddict = defaultdict(default_factory)

    @property
    def default_factory(self) -> Optional[Callable]:
        return self._ddict.default_factory

    def keys(self) -> KeysView[int]:
        return self._ddict.keys()

    def __getitem__(self, key: Union[int, slice]):
        if isinstance(key, int):
            i = key if key >= 0 else len(self) + key
            return self._ddict[i]

        elif isinstance(key, slice):
            if not (key.step is None or key.step == 1):
                raise NotImplementedError("extended slices are not supported yet")

            n = len(self)

            if key.start is None:
                start = 0
            elif key.start < 0:
                start = n + key.start
            else:
                start = key.start

            if key.stop is None:
                stop = n
            elif key.stop < 0:
                stop = n + key.stop
            else:
                stop = key.stop

            copy_range = range(start, stop)

            dlist = defaultlist()
            dlist += [self._ddict[i] for i in copy_range]

            return dlist

        else:
            name = type(key).__name__
            raise TypeError(
                f"defaultlist indices must be integers or slices, not {name}"
            )

    def __setitem__(self, key: Union[int, slice], value: Any):
        if isinstance(key, int):
            i = key if key >= 0 else len(self) + key
            self._ddict[i] = value

        elif isinstance(key, slice):
            if not (key.step is None or key.step == 1):
                raise NotImplementedError("extended slices are not supported yet")

            # 0.1 determine the current len, slice range, and value(s) to be inserted

            n = len(self)

            values = list(value) if isinstance(value, Iterable) else [value]
            nvalues = len(values)

            # 0.2 determine del range

            dstart, dstop, _ = key.indices(n)
            if dstart > dstop:
                dstop = dstart

            del_range = range(dstart, dstop)

            # 0.3 determine the insert range

            if key.start is None:
                istart = 0
            elif key.start < 0:
                istart = n + key.start
            else:
                istart = key.start

            insert_range = range(istart, istart + nvalues)

            # 1. delete elements in slice range

            indices2del = [
                i for i in self.keys() if del_range.start <= i < del_range.stop
            ]
            for i in indices2del:
                del self._ddict[i]

            # 2. update elements above slice range

            diff = nvalues - len(del_range)
            larger_indices = [i for i in self.keys() if i >= del_range.stop]
            reindexed_subdict = {i + diff: self._ddict[i] for i in larger_indices}
            for i in larger_indices:
                del self._ddict[i]
            self._ddict.update(reindexed_subdict)

            # 3. insert values safely

            for i, v in zip(insert_range, values):
                self[i] = v

        else:
            name = type(key).__name__
            raise TypeError(
                f"defaultlist indices must be integers or slices, not {name}"
            )

    # TODO support slices
    def __delitem__(self, i: int):
        del self._ddict[i]

    def __len__(self):
        if self.keys():
            return max(self.keys()) + 1
        else:
            return 0

    def __iter__(self):
        for i in range(len(self)):
            yield self._ddict[i]

    def insert(self, i: int, value: Any):
        self[i:i] = value

    def __eq__(self, other):
        if isinstance(other, Sequence):
            if len(self) != len(other):
                return False
            else:
                return all(a == b for a, b in zip(self, other))
        else:
            return False

    def __repr__(self):
        list_ = list(self[: len(self)])
        return repr(list_)

    def __str__(self):
        return f"defaultlist({self.default_factory}, {repr(self)})"


class FloorDict(dict):
    """Subclassed ``dict`` where invalid keys floor to the smallest real key

    If a key is accessed that does not exist, the nearest real key that is the
    less-than of the passed key is used.

    .. warning:: ``FloorDict`` has not been tested for production use yet
    """

    def __missing__(self, key):
        prevkey = None
        for interval, value in self.items():
            if key < interval:
                if prevkey is None:
                    raise KeyError("Passed key smaller than all real keys")
                return super().__getitem__(prevkey)
            prevkey = interval
        else:
            return super().__getitem__(prevkey)
