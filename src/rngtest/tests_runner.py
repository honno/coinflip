"""Methods used to interact with the randtests subpackage."""
from functools import wraps
from typing import Callable
from typing import Iterator
from typing import Tuple

import pandas as pd
from click import echo

from rngtest import randtests
from rngtest.randtests._exceptions import NonBinarySequenceError
from rngtest.randtests._exceptions import TestError
from rngtest.randtests._result import TestResult
from rngtest.randtests._tabulate import tabulate

__all__ = ["list_tests", "TestNotFoundError", "run_test", "run_all_tests"]


SIGLEVEL = 0.01

f_randtest_names = {
    "monobits": "Frequency (Monobits) Test",
    "frequency_within_block": "Frequency within Block Test",
    "runs": "Runs Test",
    "longest_runs": "Longest Runs in Block Test",
    "binary_matrix_rank": "Matrix Rank Test",
    "discrete_fourier_transform": "Discrete Fourier Transform (Spectral) Test",
    "non_overlapping_template_matching": "Non-Overlapping Template Matching Test",
    "overlapping_template_matching": "Overlapping Template Matching Test",
    "maurers_universal": "Maurer's Universal Test",
}


def binary_check(func):
    """Decorator to check if series comprises of binary values"""

    @wraps(func)
    def wrapper(series, *args, **kwargs):
        if series.nunique() != 2:
            raise NonBinarySequenceError()

        return func(series, *args, **kwargs)

    return wrapper


def echo_randtest_name(randtest_name):
    """Pretty print the randtest's name"""
    randtest_fname = f_randtest_names[randtest_name]
    underline = "".join("=" for char in randtest_fname)
    echo(randtest_fname + "\n" + underline)


def list_tests() -> Iterator[Tuple[str, Callable]]:
    """List all available statistical tests

    Yields
    ------
    randtest_name : `str`
        Name of statistical test
    randtest_func : `Callable`
        Function object of the statistical test
    """
    for randtest_name in randtests.__all__:
        randtest_func = getattr(randtests, randtest_name)

        yield randtest_name, randtest_func


class TestNotFoundError(ValueError):
    """Error for when a statistical test is not found"""


@binary_check
def run_test(series: pd.Series, randtest_name, **kwargs) -> TestResult:
    """Run a statistical test on RNG output

    Parameters
    ----------
    series : `Series`
        Output of the RNG being tested
    randtest_name : `str`
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
        If `randtest_name` does not match any available statistical tests
    TestError
        Errors raised when running `randtest_name`
    """
    for name, func in list_tests():
        if randtest_name == name:
            echo_randtest_name(name)

            result = func(series, **kwargs)
            echo(result)
            echo()
            echo("PASS" if result.p >= 0.01 else "FAIL")

            return result

    else:
        raise TestNotFoundError()


@binary_check
def run_all_tests(series: pd.Series) -> Iterator[Tuple[str, TestResult, Exception]]:
    """Run all available statistical test on RNG output

    Parameters
    ----------
    series : `Series`
        Output of the RNG being tested

    Yields
    ------
    randtest_name : `str`
        Name of statistical test
    result : `TestResult`
        Dataclass that contains the test's statistic and p-value as well as
        other relevant information gathered.
    exception : `NotImplementedError` or `MinimumInputError`
        The exception raised when running `randtest_name`, otherwise `None`.

    Raises
    ------
    NonBinarySequenceError
        If series contains a sequence made of non-binary values
    """
    results = {}

    for name, func in list_tests():
        echo_randtest_name(name)

        try:
            result = func(series)
            echo(result)

            yield name, result, None
            results[name] = result

        except TestError as e:
            yield name, None, e
            results[name] = None

        echo()

    table = []
    for name, result in results.items():
        f_name = f_randtest_names[name]

        if result:
            f_pvalue = result.p3f()
            success = result.p >= SIGLEVEL
            f_success = "PASS" if success else "FAIL"
        else:
            f_pvalue = 0
            f_success = "N/A"

        row = [f_name, f_pvalue, f_success]
        table.append(row)

    f_table = tabulate(
        table, ["Statistical Test", "p-value", "Result"], tablefmt="presto"
    )
    echo(f_table)
    echo((f"(significance level of {SIGLEVEL})"))
