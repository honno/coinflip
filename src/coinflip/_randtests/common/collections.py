from bisect import bisect_left
from collections import Counter
from collections import defaultdict
from collections.abc import Mapping
from collections.abc import MutableMapping
from collections.abc import MutableSequence
from functools import lru_cache
from itertools import chain
from itertools import count
from numbers import Real
from typing import Any
from typing import Callable
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

from sortedcontainers import SortedDict

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
        self._sdict = SortedDict(empty_bins)

    @property
    def intervals(self) -> Tuple[Real]:
        return tuple(self._sdict.keys())

    def __getitem__(self, key: Real):
        interval = self._roundkey(key)
        return self._sdict[interval]

    def __setitem__(self, key: Real, value: Real):
        interval = self._roundkey(key)
        self._sdict[interval] = value

    def __delitem__(self, key: Real):
        value = self._sdict[key]
        del self._sdict[key]
        self[key] += value

    def _roundkey(self, key: Real):
        return Bins.find_closest_interval(self.intervals, key)

    def __iter__(self):
        return iter(self._sdict)

    def __len__(self):
        return len(self._sdict)

    def __repr__(self):
        return str(dict(self))

    def __str__(self):
        return f"Bins({repr(self)})"

    @staticmethod
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
        self._ddict = defaultdict(default_factory or defaultlist._none_factory)

    @staticmethod
    def _none_factory() -> None:
        return None

    @property
    def default_factory(self) -> Optional[Callable]:
        return self._ddict.default_factory

    def __getitem__(self, key: Union[int, slice]):
        if isinstance(key, int):
            i = self._actualise_index(key)
            return self._ddict[i]

        elif isinstance(key, slice):
            srange = self._determine_srange(key)
            dlist = defaultlist()
            dlist += [self._ddict[i] for i in srange]
            return dlist

        else:
            defaultlist._raise_type_error(type(key))

    def __setitem__(self, key: Union[int, slice], value: Any):
        if isinstance(key, int):
            i = self._actualise_index(key)
            self._ddict[i] = value

        elif isinstance(key, slice):
            values = list(value) if isinstance(value, Iterable) else [value]
            nvalues = len(values)

            srange = self._determine_srange(key)
            if srange:
                srange_min = min(srange[0], srange[-1])
                srange_max = max(srange[0], srange[-1])
            else:
                srange_min = srange_max = srange.start

            for i in srange:
                try:
                    del self._ddict[i]
                except KeyError:
                    pass

            diff = nvalues - len(srange)
            if diff:
                keys = list(self._ddict.keys())

                threshold = srange_min + nvalues
                reindexed_subdict = {}

                mid_keys = [k for k in keys if srange_min <= k < srange_max]
                for i, k in zip(count(threshold), sorted(mid_keys)):
                    reindexed_subdict[i] = self._ddict[k]

                larger_keys = [k for k in self._ddict.keys() if k > srange_max]
                for k in larger_keys:
                    i = k + diff
                    reindexed_subdict[i] = self._ddict[k]

                self._ddict.update(reindexed_subdict)

            for i, v in zip(count(srange_min), values):
                self[i] = v

        else:
            defaultlist._raise_type_error(type(key))

    def __delitem__(self, key: Union[int, slice]):
        if isinstance(key, int):
            i = self._actualise_index(key)
            try:
                del self._ddict[i]
            except KeyError:
                pass

            larger_keys = [k for k in self._ddict.keys() if k > i]
            reindexed_subdict = {k - 1: self._ddict[k] for k in larger_keys}
            for k in larger_keys:
                del self._ddict[k]
            self._ddict.update(reindexed_subdict)

        elif isinstance(key, slice):
            srange = self._determine_srange(key)
            if srange:
                for i in srange:
                    try:
                        del self._ddict[i]
                    except KeyError:
                        pass

                srange_min = min(srange[0], srange[-1])
                srange_max = max(srange[0], srange[-1])

                reindexed_subdict = {}

                mid_keys = [
                    k for k in self._ddict.keys() if srange_min <= k < srange_max
                ]
                for i, k in zip(count(srange_min), sorted(mid_keys)):
                    reindexed_subdict[i] = self._ddict[k]

                larger_keys = [k for k in self._ddict.keys() if k > srange_max]
                for k in larger_keys:
                    i = k - len(srange)
                    reindexed_subdict[i] = self._ddict[k]

                for k in chain(mid_keys, larger_keys):
                    del self._ddict[k]
                self._ddict.update(reindexed_subdict)

        else:
            defaultlist._raise_type_error(type(key))

    def _actualise_index(self, key: int) -> int:
        if key >= 0:
            return key
        else:
            n = len(self)
            if key >= -n:
                return n + key
            else:
                raise IndexError(
                    "negative list index larger than list length, unresolvable"
                )

    def _determine_srange(self, slice_: slice) -> range:
        step = slice_.step or 1

        if slice_.start is None:
            start = 0 if step > 0 else len(self)
        else:
            start = self._actualise_index(slice_.start)

        if slice_.stop is None:
            stop = len(self) if step > 0 else 0
        else:
            stop = self._actualise_index(slice_.stop)

        return range(start, stop, step)

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

    @staticmethod
    def _raise_type_error(type_: Type):
        name = type_.__name__
        raise TypeError(f"defaultlist indices must be integers or slices, not {name}")


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
        self._sdict = SortedDict(dict)

    def __getitem__(self, key):
        keys = iter(self._sdict.keys())
        prevkey = next(keys)
        if key < prevkey:
            raise KeyError("Passed key smaller than all existing keys")

        for interval in keys:
            if key < interval:
                return self._sdict[prevkey]
            prevkey = interval
        else:
            return self._sdict[prevkey]

    def __iter__(self):
        return iter(self._sdict)

    def __len__(self):
        return len(self._sdict)
