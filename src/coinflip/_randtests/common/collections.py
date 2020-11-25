from bisect import bisect_left
from collections import Counter
from collections import OrderedDict
from collections import defaultdict
from collections.abc import Mapping
from collections.abc import MutableMapping
from collections.abc import MutableSequence
from functools import lru_cache
from numbers import Real
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
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

    def __getitem__(self, key: Union[int, slice]):
        if isinstance(key, int):
            # TODO neg
            i = key if key >= 0 else len(self) + key
            return self._ddict[i]

        elif isinstance(key, slice):
            copy_range = range(len(self))[key]

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
            # TODO neg
            i = key if key >= 0 else len(self) + key
            self._ddict[i] = value

        elif isinstance(key, slice):
            n = len(self)

            values = list(value) if isinstance(value, Iterable) else [value]
            nvalues = len(values)

            # 0 determine slice range

            start, stop, step = key.indices(n)

            # 1.1 determine del range

            dstart, dstop = start, stop

            try:
                if (dstop - dstart) / step < 0:  # diverging
                    if step >= 1:
                        dstop = dstart
                    else:
                        dstart = dstop
            except ZeroDivisionError:
                pass

            del_range = range(dstart, dstop, step)

            # 1.2 determine the insert range

            istop = start + step * nvalues
            insert_range = range(start, istop, step)

            # 2. delete keys in del range

            for i in [k for k in self._ddict.keys() if k in del_range]:
                del self._ddict[i]

            # 3. update keys above del range

            diff = nvalues - len(del_range)
            if diff:
                larger_keys = [
                    k
                    for k in self._ddict.keys()
                    if k >= max(del_range.start, del_range.stop)
                ]
                reindexed_subdict = {k + diff: self._ddict[k] for k in larger_keys}

                for k in larger_keys:
                    del self._ddict[k]
                self._ddict.update(reindexed_subdict)

            # 4. insert values safely

            for k, v in zip(insert_range, values):
                self._ddict[k] = v

        else:
            name = type(key).__name__
            raise TypeError(
                f"defaultlist indices must be integers or slices, not {name}"
            )

    # TODO support slices
    def __delitem__(self, i: int):
        del self._ddict[i]

    def __len__(self):
        if self._ddict.keys():
            return max(self._ddict.keys()) + 1
        else:
            return 0

    def __iter__(self):
        for k in range(len(self)):
            yield self._ddict[k]

    def insert(self, i: int, value: Any):
        larger_keys = [k for k in self._ddict.keys() if k >= i]
        reindexed_subdict = {k + 1: self._ddict[k] for k in larger_keys}
        for k in larger_keys:
            del self._ddict[k]
        self._ddict.update(reindexed_subdict)

        self._ddict[i] = value

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


class FloorDict(Mapping):
    """Mapping where invalid keys floor to the smallest real key

    If a key is accessed that does not exist, the nearest real key that is the
    less-than of the passed key is used.

    Parameters
    ----------
    dict : ``Dict``
        Dictionary containing the key-value pairs to be floored to
    """

    def __init__(self, dict: Dict):
        self._odict = OrderedDict(dict)

    def __getitem__(self, key):
        keys = iter(self._odict.keys())
        prevkey = next(keys)
        if key < prevkey:
            raise KeyError("Passed key smaller than all existing keys")

        for interval in keys:
            if key < interval:
                return self._odict[prevkey]
            prevkey = interval
        else:
            return self._odict[prevkey]

    def __iter__(self):
        return iter(self._odict)

    def __len__(self):
        return len(self._odict)
