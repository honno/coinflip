from typing import NamedTuple

from .randomness_testsuite.RunTest import RunTest


class StevenResult(NamedTuple):
    p: float
    result: bool


def runs_test(bits):
    bits_str = "".join(str(bit) for bit in bits)
    result = RunTest.run_test(bits_str)

    return StevenResult(*result)
