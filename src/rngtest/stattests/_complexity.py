from rngtest.stattests._common import TestResult
from rngtest.stattests._common import stattest

__all__ = ["linear_complexity"]


@stattest()
def linear_complexity(series, blocksize):
    n = len(series)
    print(n)
    print(series)

    return TestResult(statistic=None, p=None)
