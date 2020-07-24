from coinflip.randtests._decorators import randtest
from coinflip.randtests._result import TestResult

__all__ = ["linear_complexity"]


@randtest()
def linear_complexity(series, blocksize):
    n = len(series)
    print(n)
    print(series)

    return TestResult(statistic=None, p=None)
