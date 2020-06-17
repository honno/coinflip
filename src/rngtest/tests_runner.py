import pandas as pd

from rngtest import stattests

__all__ = ["list_tests", "run_test", "run_all_tests"]


def list_tests():
    for stattest_name in stattests.__all__:
        stattest_func = getattr(stattests, stattest_name)

        yield stattest_name, stattest_func


def run_test(series: pd.Series, stattest_name):
    for name, func in list_tests():
        if stattest_name == name:
            result = func(series)

            return result

    else:
        raise ValueError()


def run_all_tests(series: pd.Series):
    if series.nunique() == 2:
        for name, func in list_tests():
            result = func(series)

            yield name, result

    else:
        raise NotImplementedError()
