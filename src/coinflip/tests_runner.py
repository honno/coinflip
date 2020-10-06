"""Methods used to interact with the randtests subpackage."""
from functools import wraps
from typing import Callable
from typing import Iterator
from typing import Tuple

import pandas as pd

from coinflip import console
from coinflip import randtests
from coinflip.randtests._exceptions import NonBinarySequenceError
from coinflip.randtests._exceptions import TestError
from coinflip.randtests._result import TestResult

__all__ = ["list_tests", "TestNotFoundError", "run_test", "run_all_tests"]


SIGLEVEL = 0.01

f_randtest_names = {
    "monobit": "Frequency (Monobit) Test",
    "frequency_within_block": "Frequency within Block Test",
    "runs": "Runs Test",
    "longest_runs": "Longest Runs in Block Test",
    "binary_matrix_rank": "Matrix Rank Test",
    "spectral": "Discrete Fourier Transform (Spectral) Test",
    "non_overlapping_template_matching": "Non-Overlapping Template Matching Test",
    "overlapping_template_matching": "Overlapping Template Matching Test",
    "maurers_universal": "Maurer's Universal Test",
    #
    "approximate_entropy": "Approximate Entropy Test",
}


def binary_check(func):
    """Decorator to check if series comprises of binary values"""

    @wraps(func)
    def wrapper(series, *args, **kwargs):
        if series.nunique() != 2:
            raise NonBinarySequenceError()

        return func(series, *args, **kwargs)

    return wrapper


def print_randtest_name(randtest_name):
    """Pretty print the randtest's name"""
    randtest_fname = f_randtest_names[randtest_name]
    console.print(randtest_fname, style="bold")
    console.print("".join("─" for char in randtest_fname))


def list_tests() -> Iterator[Tuple[str, Callable]]:
    """List all available statistical tests

    Yields
    ------
    randtest_name : ``str``
        Name of statistical test
    randtest_func : ``Callable``
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
    series : ``Series``
        Output of the RNG being tested
    randtest_name : ``str``
        Name of statistical test
    **kwargs
        Keyword arguments to pass to statistical test

    Returns
    -------
    result : ``TestResult`` or ``MultiTestResult``
        Data containers of the test's result(s).

    Raises
    ------
    TestNotFoundError
        If `randtest_name` does not match any available statistical tests
    TestError
        Errors raised when running ``randtest_name``
    """
    for name, func in list_tests():
        if randtest_name == name:
            print_randtest_name(name)

            result = func(series, **kwargs)
            console.print(result)

            return result

    else:
        raise TestNotFoundError()


@binary_check
def run_all_tests(series: pd.Series) -> Iterator[Tuple[str, TestResult, Exception]]:
    """Run all available statistical test on RNG output

    Parameters
    ----------
    series : ``Series``
        Output of the RNG being tested

    Yields
    ------
    randtest_name : ``str``
        Name of statistical test
    result : ``TestResult`` or ``MultiTestResult``
        Data containers of the test's result(s)
    exception : ``NotImplementedError`` or ``MinimumInputError``
        The exception raised when running ``randtest_name``, otherwise ``None``.

    Raises
    ------
    NonBinarySequenceError
        If series contains a sequence made of non-binary values
    """
    results = {}

    for name, func in list_tests():
        print_randtest_name(name)

        try:
            result = func(series)
            console.print(result)

            yield name, result, None
            results[name] = result

        except TestError as e:
            yield name, None, e
            results[name] = None

        console.print()

    # TODO print a table
    # f_table = Table(box=box.DOUBLE)
    # f_table.add_column("Statistical Test", justify="left")
    # f_table.add_column("p-value", justify="right")
    # f_table.add_column("Verdict", justify="right")
    # for name, result in results.items():
    #     f_name = f_randtest_names[name]

    #     if result:
    #         f_pvalue = str(round(result.p, 3))
    #         f_pvalue += "0" * (5 - len(f_pvalue))  # zero pad

    #         success = result.p >= SIGLEVEL
    #         verdict = "PASS" if success else "FAIL"
    #         colour = "green" if success else "red"
    #         f_verdict = Text(verdict, style=colour)
    #     else:
    #         f_pvalue = "-"
    #         f_verdict = Text("N/A", style="yellow")

    #     f_table.add_row(f_name, f_pvalue, f_verdict)

    # console.print(f_table)
