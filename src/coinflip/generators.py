"""Generators of binary sequences

Objects infinitely generate ``0`` and ``1`` integers to represent a binary sequence."""
from collections.abc import Iterator
from random import Random

__all__ = ["Python"]


class Python(Iterator):
    def __init__(self):
        self._rng = Random()

    def __next__(self):
        return self._rng.getrandbits(1)
