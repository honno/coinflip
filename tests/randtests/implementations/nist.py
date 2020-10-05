import sts

from ._implementation import Implementation


def monobit(bits):
    return sts.frequency(bits)


def linear_complexity(bits, blocksize):
    return sts.linear_complexity(bits, blocksize)


def cusum(bits, reverse=False):
    return sts.cumulative_sums(bits, reverse=reverse)


def random_excursions(bits):
    return sts.random_excursions(bits)


testmap = {
    "monobit": Implementation(monobit),
    "linear_complexity": Implementation(linear_complexity),
    "cusum": Implementation(cusum),
    "random_excursions": Implementation(random_excursions),
}
