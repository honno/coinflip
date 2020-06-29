import warnings
from typing import Callable
from typing import Dict
from typing import Iterator
from typing import Tuple

import pandas as pd
from click import echo
from colorama import Fore
from colorama import init
from tabulate import tabulate

from rngtest import stattests
from rngtest.stattests._common import TestResult
from rngtest.stattests._common import dim
from rngtest.stattests._common.exceptions import MinimumInputError
from rngtest.stattests._common.exceptions import NonBinarySequenceError

__all__ = ["TEST_EXCEPTION", "list_tests", "run_test", "run_all_tests"]

init()

warn_txt = Fore.YELLOW + "WARN" + Fore.RESET
err_txt = Fore.RED + "ERR!" + Fore.RESET


def formatwarning(msg, *args, **kwargs):
    return dim(f"{warn_txt} {msg}\n")


warnings.formatwarning = formatwarning


def echo_err(error: Exception):
    line = f"{err_txt} {error}\n"
    echo(line)


def binary_check(func):
    def wrapper(series, *args, **kwargs):
        if series.nunique() != 2:
            error = NonBinarySequenceError()
            echo_err(error)
            raise error

        return func(series, *args, **kwargs)

    return wrapper


TEST_EXCEPTION = (NotImplementedError, MinimumInputError)


signifigance_level = 0.01

f_stattest_names = {
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


def echo_stattest_name(stattest_name):
    stattest_fname = f_stattest_names[stattest_name]
    underline = "".join("-" for char in stattest_fname)
    echo(stattest_fname + "\n" + underline)


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


@binary_check
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
            echo_stattest_name(name)

            try:
                result = func(series, **kwargs)
            except TEST_EXCEPTION as e:
                echo_err(e)
                raise e

            echo(result)

            echo("PASS" if result.p >= 0.01 else "FAIL")

            return result

    else:
        raise TestNotFoundError()


@binary_check
def run_all_tests(series: pd.Series) -> Dict[str, TestResult]:
    """Run all available statistical test on RNG output

    Parameters
    ----------
    series : `Series`
        Output of the RNG being tested

    Returns
    -------
    results : `Dict[str, TestResult]`
        Name of statistical test mapped to given result.

    Raises
    ------
    NonBinarySequenceError
        If series contains a sequence made of non-binary values
    """
    results = {}

    for name, func in list_tests():
        echo_stattest_name(name)

        try:
            result = func(series)
            echo(result)

            echo()

            results[name] = result

        except TEST_EXCEPTION as e:
            echo_err(e)

    f_names = [f_stattest_names[name] for name in results.keys()]
    f_pvalues = [result.p3f() for result in results.values()]

    f_successes = []
    for result in results.values():
        success = result.p >= signifigance_level
        msg = "PASS" if success else "FAIL"
        f_successes.append(msg)

    f_table = tabulate(
        zip(f_names, f_pvalues, f_successes), ["Statistical Test", "p-value", "Result"]
    )
    echo(f"\n\n{f_table}")

    return results
