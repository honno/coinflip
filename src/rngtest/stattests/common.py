from dataclasses import dataclass
from functools import wraps

import pandas as pd

__all__ = ["TestResult", "stattest", "binary_stattest"]


@dataclass
class TestResult:
    p: float

    def p2f(self):
        return round(self.p, 2)

    def __str__(self):
        raise NotImplementedError()

    def report(self):
        raise NotImplementedError()


def stattest(func):
    @wraps(func)
    def wrapper(series: pd.Series):
        if series.nunique() == 1:
            raise ValueError()

        result = func(series)

        return result

    return wrapper


def binary_stattest(func):
    @wraps(func)
    def wrapper(series: pd.Series):
        if series.nunique() != 2:
            raise ValueError()

        result = func(series)

        return result

    return wrapper
