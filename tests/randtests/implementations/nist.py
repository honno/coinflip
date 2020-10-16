import sts

from ._implementation import Implementation


def monobit(bits):
    return sts.frequency(bits)


def linear_complexity(bits, blocksize):
    return sts.linear_complexity(bits, blocksize)


def serial(bits, blocksize):
    return sts.serial(bits, blocksize)


def cusum(bits, reverse=False):
    return sts.cumulative_sums(bits, reverse=reverse)


def random_excursions(bits):
    return sts.random_excursions(bits)


def random_excursions_variant(bits):
    return sts.random_excursions_variant(bits)


testmap = {
    "monobit": Implementation(monobit),
    "linear_complexity": Implementation(linear_complexity),
    "serial": Implementation(serial),
    "cusum": Implementation(cusum),
    "random_excursions": Implementation(random_excursions),
    "random_excursions_variant": Implementation(random_excursions_variant),
}
