from typing import NamedTuple

from .sp800_22_tests import sp800_22_monobit_test


class DJResult(NamedTuple):
    success: bool
    p: float
    unknown: None


def monobit_test(bits):
    result = sp800_22_monobit_test.monobit_test(bits)

    return DJResult(*result)
