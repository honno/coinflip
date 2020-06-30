from rngtest.stattests._decorators import stattest
from rngtest.stattests._result import TestResult

__all__ = ["linear_complexity"]


@stattest()
def linear_complexity(series, blocksize):
    n = len(series)
    print(n)
    print(series)

    return TestResult(statistic=None, p=None)
