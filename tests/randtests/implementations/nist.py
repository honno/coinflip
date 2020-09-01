from sts import *

from ._implementation import Implementation


def monobit(bits):
    return frequency(bits)


testmap = {
    "monobit": Implementation(monobit),
}
