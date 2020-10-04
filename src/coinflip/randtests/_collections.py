# TODO test non-ordered inputs, subclass OrderedDict
from bisect import bisect_left
from typing import Iterable

__all__ = ["FloorDict", "Bins"]


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
