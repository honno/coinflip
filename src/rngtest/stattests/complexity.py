from rngtest.stattests.common.decorators import binary_stattest
from rngtest.stattests.common.result import TestResult

__all__ = ["linear_complexity"]


@binary_stattest
def linear_complexity(series, block_size):
    n = len(series)
    print(n)
    print(series)

    return TestResult(statistic=None, p=None)
