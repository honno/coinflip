"""Methods used to interact with the _randtests subpackage."""
from functools import wraps
from shutil import get_terminal_size
from typing import Callable
from typing import Dict
from typing import Iterator
from typing import Tuple

import pandas as pd
from rich import box
from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import TextColumn
from rich.progress import TimeRemainingColumn
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from coinflip import _randtests
from coinflip._randtests.common.exceptions import NonBinarySequenceError
from coinflip._randtests.common.exceptions import TestError
from coinflip._randtests.common.result import BaseTestResult
from coinflip._randtests.common.result import MultiTestResult
from coinflip._randtests.common.result import TestResult
from coinflip.cli import console
from coinflip.cli.pprint import print_error
from coinflip.cli.pprint import print_warning

__all__ = [
    "list_tests",
    "TestNotFoundError",
    "run_test",
    "run_all_tests",
    "print_results",
]


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
    "linear_complexity": "Linear Complexity Test",
    "serial": "Serial Test",
    "approximate_entropy": "Approximate Entropy Test",
    "cusum": "Cumulative Sums (Cusum) Test",
    "random_excursions": "Random Excursions Test",
    "random_excursions_variant": "Random Excursions Variant Test",
}


f_randtest_abbreviations = {
    "monobit": "Monobit",
    "frequency_within_block": "Block Freq.",
    "runs": "Runs",
    "longest_runs": "Longest Runs",
    "binary_matrix_rank": "Matrix",
    "spectral": "Spectral",
    "non_overlapping_template_matching": "Non-Overlap.",
    "overlapping_template_matching": "Overlapping",
    "maurers_universal": "Universal",
    "linear_complexity": "Complexity",
    "serial": "Serial",
    "approximate_entropy": "Entropy",
    "cusum": "Cusum",
    "random_excursions": "Excursions",
    "random_excursions_variant": "Excur. Var.",
}


def binary_check(func):
    """Decorator to check if series comprises of binary values"""

    @wraps(func)
    def wrapper(series, *args, **kwargs):
        if series.nunique() != 2:
            raise NonBinarySequenceError()

        return func(series, *args, **kwargs)

    return wrapper


def print_randtest_name(randtest_name: str, color: str):
    """Pretty print the randtest's name"""
    size = get_terminal_size()
    ncols = min(size.columns, 80)

    randtest_fname = f_randtest_names[randtest_name]

    color = f"bright_{color}"

    rule = Rule(randtest_fname, style=color)
    console.print(rule, width=ncols)


def list_tests() -> Iterator[Tuple[str, Callable]]:
    """List all available statistical tests

    Yields
    ------
    randtest_name : ``str``
        Name of statistical test
    randtest_func : ``Callable``
        Function object of the statistical test
    """
    for randtest_name in _randtests.__all__:
        randtest_func = getattr(_randtests, randtest_name)

        yield randtest_name, randtest_func


class TestNotFoundError(ValueError):
    """Error for when a statistical test is not found"""


columns = (
    TextColumn("[progress.description]{task.description}"),
    BarColumn(bar_width=54),  # i.e. progress is roughly 80 cols wide overall
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    TimeRemainingColumn(),
)


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
    try:
        func = getattr(_randtests, randtest_name)
    except AttributeError as e:
        raise TestNotFoundError() from e

    with Progress(*columns, console=console, transient=True) as progress:
        abbrv = f_randtest_abbreviations[randtest_name]
        task = progress.add_task(abbrv)

        try:
            result = func(series, ctx=(progress, task), **kwargs)

            color = "yellow" if result.failures else "green"
            print_randtest_name(randtest_name, color)
            console.print(result)

            return result

        except TestError as e:
            print_randtest_name(randtest_name, "red")
            print_error(e)

            raise e


@binary_check
def run_all_tests(series: pd.Series) -> Iterator[Tuple[str, TestResult, Exception]]:
    """Run all available statistical test on RNG output

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
    with Progress(*columns, console=console, transient=True) as progress:
        names, funcs = zip(*list_tests())
        tasks = []
        for name in names:
            abbrv = f_randtest_abbreviations[name]
            task = progress.add_task(abbrv, start=False)

            tasks.append(task)

        results = {}
        for name, func, task in zip(names, funcs, tasks):
            progress.start_task(task)

            try:
                result = func(series, ctx=(progress, task))

                color = "yellow" if result.failures else "green"

                print_randtest_name(name, color)
                console.print(result)

                yield name, result, None

                results[name] = result

            except TestError as e:
                progress.update(task, completed=True)

                print_randtest_name(name, "red")
                print_error(e)

                yield name, None, e

                results[name] = None

            console.print("")

    print_results_summary(results)


def print_results(results: Dict[str, BaseTestResult]):
    for name, result in results.items():
        color = "yellow" if result.failures else "green"

        print_randtest_name(name, color)
        console.print(result)
        console.print("")

    print_results_summary(results)


def print_results_summary(results: Dict[str, BaseTestResult]):
    size = get_terminal_size()
    ncols = min(size.columns, 80)

    rule = Rule("Test Results Summary", style="bright_blue")
    console.print(rule, width=ncols)

    unsummarisable_fnames = []

    table = Table(box=box.DOUBLE, caption=f"using a significance level of {SIGLEVEL}")
    table.add_column("Statistical Test", justify="eft")
    table.add_column("p-value", justify="left")
    table.add_column("Verdict", justify="left")
    for name, result in results.items():
        f_name = f_randtest_names[name]

        if isinstance(result, MultiTestResult):
            unsummarisable_fnames.append(f_name)
            continue

        if result:
            f_pvalue = str(round(result.p, 3))
            f_pvalue += "0" * (5 - len(f_pvalue))  # zero pad

            success = result.p >= SIGLEVEL
            verdict = "PASS" if success else "FAIL"
            colour = "green" if success else "red"
            f_verdict = Text(verdict, style=colour)
        else:
            f_pvalue = "-"
            f_verdict = Text("N/A", style="yellow")

        table.add_row(f_name, f_pvalue, f_verdict)

    if unsummarisable_fnames:
        warn_msg = "Multiple test results are currently not summarisable:\n"
        warn_msg += "\n".join(f"  • {f_name}" for f_name in unsummarisable_fnames)
        print_warning(warn_msg)

        console.print("")

    console.print(table)
