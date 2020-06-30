from collections import UserDict

__all__ = ["FloorDict"]


class FloorDict(UserDict):
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
