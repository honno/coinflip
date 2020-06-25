from math import sqrt
from random import getrandbits

__all__ = ["primes", "python"]


def python():
    while True:
        yield getrandbits(1)


def numbers(start=1):
    n = start
    while True:
        yield n
        n += 1


def primes():
    yield 0  # n=1
    yield 1  # n=2

    for n in numbers(3):
        if n % 2 == 0:
            yield 0
        else:
            for divisor in range(3, int(sqrt(n)) + 1, 2):
                if n % divisor == 0:
                    yield 0
            else:
                yield 1
