from shutil import get_terminal_size

import pandas as pd
from click import Choice
from click import Path
from click import argument
from click import group
from click import option

from coinflip import console
from coinflip import generators
from coinflip._parsing import *
from coinflip._pprint import *
from coinflip._runner import *
from coinflip.exceptions import NonBinarySequenceError
from coinflip.exceptions import TestError
from coinflip.randtests import __all__ as randtest_names

__all__ = [
    "run",
    "example_run",
]


# TODO descriptions of the series e.g. length
def print_series(series):
    """Pretty print series that contain binary data"""
    size = get_terminal_size()
    ncols = min(size.columns, 80)

    console.print(pretty_sequence(series, ncols))


# TODO extend Choice to use print_error and newline-delimit lists
test_choice = Choice(randtest_names)


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

help_msg = {
    "name": "Specify name of the store.",
    "dtype": "Specify data type of the data.",
    "test": "Specify single test to run on data.",
}


@group(context_settings=CONTEXT_SETTINGS)
def main():
    """Randomness tests for RNG output.

    Randomness tests can be ran on the your binary data via the run command.
    Rich documents explaining the test results can be produced via the report
    command.
    """


@main.command()
@argument("data", type=Path(exists=True))
@option("-t", "--test", type=test_choice, help=help_msg["test"], metavar="<test>")
def run(data, test):
    """Run randomness tests on DATA."""
    try:
        series = parse_data(data)
        print_series(series)
    except (DataParsingError, NonBinarySequenceError) as e:
        print_error(e)
        exit(1)

    if not test:
        for name, result, e in run_all_tests(series):
            pass

    else:
        try:
            run_test(series, test)
        except TestError:
            exit(1)


@main.command()
@option(
    "-e",
    "--example",
    type=Choice(generators.__all__),
    default="python",
    help="Example binary output to use.",
    metavar="<example>",
)
@option("-n", "--length", type=int, default=512, help="Length of binary output.")
@option("-t", "--test", type=test_choice, help=help_msg["test"], metavar="<test>")
def example_run(example, length, test):
    """Run randomness tests on example data."""
    generator_func = getattr(generators, example)
    generator = generator_func()

    series = pd.Series(next(generator) for _ in range(length))
    series = series.infer_objects()
    print_series(series)
    console.print()

    if not test:
        for name, result, e in run_all_tests(series):
            pass

    else:
        try:
            run_test(series, test)
        except TestError:
            exit(1)
