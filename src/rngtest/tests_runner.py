from typing import Callable
from typing import Iterator
from typing import Tuple

import pandas as pd

from rngtest import stattests
from rngtest.stattests._common import NonBinarySequenceError
from rngtest.stattests._common import TestResult

__all__ = ["list_tests", "run_test", "run_all_tests"]


def list_tests() -> Iterator[Tuple[str, Callable]]:
    """List all available statistical tests

    Yields
    ------
    stattest_name : `str`
        Name of statistical test
    stattest_func : `Callable`
        Function object of the statistical test
    """
    for stattest_name in stattests.__all__:
        stattest_func = getattr(stattests, stattest_name)

        yield stattest_name, stattest_func


class TestNotFoundError(ValueError):
    """Error for when a statistical test is not found"""

    pass


def run_test(series: pd.Series, stattest_name, **kwargs) -> TestResult:
    """Run a statistical test on RNG output

    Parameters
    ----------
    series : `Series`
        Output of the RNG being tested
    stattest_name : `str`
        Name of statistical test
    **kwargs
        Keyword arguments to pass to statistical test

    Returns
    -------
    result : `TestResult`
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.

    Raises
    ------
    TestNotFoundError
        If `stattest_name` does not match any available statistical tests
    """
    for name, func in list_tests():
        if stattest_name == name:
            result = func(series, **kwargs)

            return result

    else:
        raise TestNotFoundError()


def run_all_tests(series: pd.Series) -> Iterator[Tuple[str, TestResult]]:
    """Run all available statistical test on RNG output

    Parameters
    ----------
    series : `Series`
        Output of the RNG being tested

    Yields
    -------
    stattest_name : `str`
        Name of statistical test for given result
    result : `TestResult`
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.

    Raises
    ------
    NonBinarySequenceError
        If series contains a sequence made of non-binary values
    """
    if series.nunique() == 2:
        for name, func in list_tests():
            result = func(series)

            yield name, result

    else:
        raise NonBinarySequenceError()
