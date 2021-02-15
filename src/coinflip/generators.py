"""Generators of binary sequences

Objects infinitely generate ``0`` and ``1`` integers to represent a binary sequence."""
from collections.abc import Iterator
from random import Random

__all__ = ["Python", "Mersenne"]


class Python(Iterator):
    def __init__(self):
        self._rng = Random()

    def __next__(self):
        return self._rng.getrandbits(1)


class Mersenne(Iterator):
    def __init__(self, seed=42):
        self.seed = seed
        self.j = 2 ** 31 - 1
        self.k = 16807
        self.period = 2 ** 30

    def __next__(self):
        self.seed = (self.k * self.seed) % self.j
        if self.seed / self.j < 0.50:
            return 0
        else:
            return 1
