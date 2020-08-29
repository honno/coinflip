from sts import *

from ._implementation import Implementation


def monobit(bits):
    n = len(bits)
    return Frequency(bits, n)


testmap = {
    "monobit": Implementation(monobit),
}
