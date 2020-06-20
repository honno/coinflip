import random
from math import sqrt

__all__ = ["primes", "python"]


def python():
    while True:
        yield random.choice([True, False])


def natural_numbers():
    n = 1

    while True:
        yield n
        n += 1


def is_prime(n):
    if n == 2:
        return True
    if n % 2 == 0 or n <= 1:
        return False

    for divisor in range(3, int(sqrt(n)) + 1, 2):
        if n % divisor == 0:
            return False

    return True


def primes():
    for n in natural_numbers():
        yield is_prime(n)
