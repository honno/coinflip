# TODO test non-ordered inputs, subclass OrderedDict
from typing import Iterable

__all__ = ["FloorDict", "RoundingDict", "Bins"]


class FloorDict(dict):
    """Subclassed `dict` where invalid keys floor to the smallest real key

    If a key is accessed that does not exist, the nearest real key that is the
    less-than of the passed key is used.
    """

    def __missing__(self, key):
        prevkey = None
        for realkey, value in self.items():
            if key < realkey:
                if prevkey is None:
                    raise KeyError()
                return super().__getitem__(prevkey)
            prevkey = realkey
        else:
            return super().__getitem__(prevkey)


class RoundingDict(dict):
    """Subclassed `dict` where invalid keys are rounded to the nearest real key

    If a key is accessed that does not exist, the nearest real key to the passed
    key is used.
    """

    def _roundkey(self, key):
        realkeys = list(self.keys())
        minkey = realkeys[0]
        midkeys = realkeys[1:-1]
        maxkey = realkeys[-1]

        if key <= minkey:
            return minkey
        elif key >= maxkey:
            return maxkey
        elif key in midkeys:
            return key
        else:
            raise KeyError()

    def __setitem__(self, key, value):
        realkey = self._roundkey(key)
        super().__setitem__(realkey, value)

    def __getitem__(self, key):
        realkey = self._roundkey(key)
        return super().__getitem__(realkey)


class Bins(RoundingDict):
    """Subclassed `RoundingDict` to initialise intervals as empty bins"""

    def __init__(self, intervals: Iterable[int]):
        """Initialise intervals as keys to values of 0"""
        empty_bins = {interval: 0 for interval in intervals}
        super().__init__(empty_bins)
