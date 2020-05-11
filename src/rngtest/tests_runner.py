import pandas as pd
from click import echo

from rngtest.stattests import frequency
from rngtest.stattests import runs

__all__ = ["ls_tests", "run_test", "run_all_tests"]

BINARY_STATTESTS = [
    frequency.monobits,
    frequency.frequency_within_block,
    runs.runs,
]

STATTESTS = [frequency.frequency]


def ls_tests():
    for stattest in BINARY_STATTESTS + STATTESTS:
        name = stattest.__name__

        yield name


def run_test(series: pd.Series, stattest_str):
    for func in STATTESTS:
        if stattest_str == func.__name__:
            _run_test(series, func)
            break


def _run_test(series, stattest):
    echo(stattest.__name__)
    result = stattest(series)
    echo(str(result))


def run_all_tests(series: pd.Series):
    if series.nunique() == 2:
        for stattest in BINARY_STATTESTS:
            _run_test(series, stattest)
    else:
        for stattest in STATTESTS:
            _run_test(series, stattest)
