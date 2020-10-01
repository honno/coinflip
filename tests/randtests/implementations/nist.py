import sts

from ._implementation import Implementation


def monobit(bits):
    return sts.frequency(bits)


def linear_complexity(bits, blocksize):
    return sts.linear_complexity(bits, blocksize)


testmap = {
    "monobit": Implementation(monobit),
    "linear_complexity": Implementation(linear_complexity),
}
