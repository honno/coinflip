from rngtest.stattests.common import TestResult
from rngtest.stattests.common import binary_stattest

__all__ = ["linear_complexity"]


@binary_stattest
def linear_complexity(series, block_size):
    n = len(series)
    print(n)
    print(series)

    return TestResult(statistic=None, p=None)
