import pandas as pd

from rngtest.stattests import frequency
from rngtest.stattests import runs

__all__ = ["list_tests", "run_test", "run_all_tests"]

STATTESTS = [
    frequency.monobits,
    frequency.frequency_within_block,
    runs.runs,
]


def list_tests():
    for stattest in STATTESTS:
        name = stattest.__name__

        yield name


def run_test(series: pd.Series, stattest_str):
    for func in STATTESTS:
        if stattest_str == func.__name__:
            result = _run_test(series, func)
            return result
    else:
        raise ValueError()


def _run_test(series, stattest):
    result = stattest(series)

    return result


def run_all_tests(series: pd.Series):
    if series.nunique() == 2:
        for stattest in STATTESTS:
            result = _run_test(series, stattest)
            yield result
    else:
        raise NotImplementedError()
