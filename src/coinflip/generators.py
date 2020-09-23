"""Generators of binary sequences

Methods infinitely generate ``0`` and ``1`` integers to represent a binary sequence."""
from math import sqrt
from random import getrandbits

__all__ = ["python", "primes"]


def python():
    """Generates random bits using python's ``random`` module

    Yields
    ------
    bit : ``0`` or `1`
        Random bit

    See Also
    --------
    random.getrandbits : Method used to generate bits
    """
    while True:
        yield getrandbits(1)


def numbers(start=1):
    """Generates natural numbers

    Parameters
    ----------
    start : ``int``, default ``1``
        Starting number to count up from

    Yields
    ------
    n : ``int``
        Natural number
    """
    n = start
    while True:
        yield n
        n += 1


def primes():
    """Generates bits representing if natural numbers are prime

    Yields
    ------
    bit: ``0`` or ``1``
        Whether next number is prime: ``0`` represents number is a composite (i.e.
        not a prime), ``1`` represents number is a prime.
    """
    yield 0  # n = 1
    yield 1  # n = 2

    for n in numbers(3):
        if n % 2 == 0:
            yield 0
        else:
            for divisor in range(3, int(sqrt(n)) + 1, 2):
                if n % divisor == 0:
                    yield 0
            else:
                yield 1
