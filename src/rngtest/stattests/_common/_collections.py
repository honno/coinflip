from collections import UserDict

__all__ = ["FloorDict"]


class KeyTooSmallError(ValueError):
    pass


class FloorDict(UserDict):
    def __getitem__(self, key):
        try:
            return self.data[key]
        except KeyError:
            prevkey = None
            for realkey, value in self.data.items():
                if key < realkey:
                    if prevkey is None:
                        raise KeyTooSmallError()
                    else:
                        return self.data[prevkey]
                else:
                    prevkey = realkey

            else:
                return self.data[prevkey]
