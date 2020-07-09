__all__ = ["floordict"]


# TODO test non-ordered inputs
class floordict(dict):
    """Subclassed `dict` where invalid keys floor to the smallest real key

    If a `floordict` is passed a missing key, the nearest real key that is the
    less-than of the passed key is used.
    """

    def __missing__(self, key):
        prevkey = None
        for realkey, value in self.items():
            if key < realkey:
                if prevkey is None:
                    raise KeyError()
                return dict.__getitem__(self, prevkey)
            prevkey = realkey
        else:
            return dict.__getitem__(self, prevkey)
