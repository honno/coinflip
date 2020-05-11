from typing import NamedTuple

from .sp800_22_tests import sp800_22_frequency_within_block_test
from .sp800_22_tests import sp800_22_monobit_test
from .sp800_22_tests import sp800_22_runs_test


class DJResult(NamedTuple):
    success: bool
    p: float
    unknown: None


def monobit_test(bits):
    result = sp800_22_monobit_test.monobit_test(bits)

    return DJResult(*result)


block_size = 20


def frequency_within_block_test(bits):
    result = sp800_22_frequency_within_block_test.frequency_within_block_test(bits)

    return DJResult(*result)


def runs_test(bits):
    result = sp800_22_runs_test.runs_test(bits)

    return DJResult(*result)
