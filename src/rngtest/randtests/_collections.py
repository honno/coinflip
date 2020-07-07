from collections import UserDict

__all__ = ["FloorDict"]


# TODO ensure key order ala OrderedDic
class FloorDict(UserDict):
    """Dict where invalid keys floor to the smallest real key

    If `__getitem__` is passed a non-existent key, `FloorDict` attempts to find
    a real key that is the nearest less-than of the passed key.
    """

    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            prevkey = None
            for realkey, value in self.data.items():
                if key < realkey:
                    if prevkey is None:
                        raise KeyError()
                    return self.data[prevkey]
                prevkey = realkey
            else:
                return self.data[prevkey]
