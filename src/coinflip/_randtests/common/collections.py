# TODO test non-ordered inputs, subclass OrderedDict
from bisect import bisect_left
from collections import defaultdict
from collections.abc import MutableSequence
from typing import Iterable

__all__ = ["FloorDict", "Bins", "defaultlist"]


class FloorDict(dict):
    """Subclassed ``dict`` where invalid keys floor to the smallest real key

    If a key is accessed that does not exist, the nearest real key that is the
    less-than of the passed key is used.
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


class Bins(dict):
    """Subclassed ``dict`` to initialise intervals as empty bins

    If a key is accessed that does not exist, the nearest real key to the passed
    key is used.
    """

    def __init__(self, intervals: Iterable[int]):
        """Initialise intervals as keys to values of 0"""
        empty_bins = {interval: 0 for interval in intervals}
        self.realkeys_cache = {}
        super().__init__(empty_bins)

    def __setitem__(self, key, value):
        realkey = self._roundkey(key)
        super().__setitem__(realkey, value)

    def __getitem__(self, key):
        realkey = self._roundkey(key)
        return super().__getitem__(realkey)

    def _roundkey(self, key):
        try:
            realkey = self.realkeys_cache[key]
            return realkey
        except KeyError:
            pass

        realkeys = list(self.keys())
        minkey = realkeys[0]
        midkeys = realkeys[1:-1]
        maxkey = realkeys[-1]

        if key <= minkey:
            realkey = minkey
        elif key >= maxkey:
            realkey = maxkey
        elif key in midkeys:
            realkey = key
        else:
            i = bisect_left(realkeys, key)
            leftkey = realkeys[i - 1]
            rightkey = realkeys[i]

            if leftkey - key > rightkey - key:
                realkey = leftkey
            else:
                realkey = rightkey

        self.realkeys_cache[key] = realkey
        return realkey


class defaultlist(MutableSequence):
    def __init__(self, default_factory):
        self._defaultdict = defaultdict(default_factory)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._defaultdict[key]

        elif isinstance(key, slice):
            indices = range(key.start or 1, key.stop, key.step or 1)
            return [self[i] for i in indices]

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._defaultdict[key] = value

        elif isinstance(key, slice):
            raise NotImplementedError()  # TODO

    def __delitem__(self, i):
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

    def insert(self, key, value):
        if key < len(self):
            indices = self._defaultdict.keys()
            larger_indexes = [i for i in indices if i >= key]
            reindexed_subdict = {i + 1: self._defaultdict[i] for i in larger_indexes}
            for i in larger_indexes:
                del self._defaultdict[i]
            self._defaultdict.update(reindexed_subdict)

        self._defaultdict[key] = value

    def append(self, value):
        self.insert(len(self), value)
