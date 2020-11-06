import pandas as pd
from click import Choice
from click import Path
from click import argument
from click import group
from click import option

from coinflip import generators
from coinflip._randtests.common.exceptions import NonBinarySequenceError
from coinflip._randtests.common.exceptions import TestError
from coinflip.cli import console
from coinflip.cli.parsing import DataParsingError
from coinflip.cli.parsing import *
from coinflip.cli.pprint import *
from coinflip.cli.report import *
from coinflip.cli.runner import *
from coinflip.randtests import __all__ as randtest_names

__all__ = ["run", "example_run", "read", "report"]


# TODO extend Choice to use print_error and newline-delimit lists
test_choice = Choice(randtest_names)


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@group(context_settings=CONTEXT_SETTINGS)
def main():
    """Randomness tests for RNG output.

    Randomness tests can be ran on the your binary data via the run command.
    Rich documents explaining the test results can be produced via the report
    command.
    """


@main.command()
@argument("data", type=Path(exists=True))
@argument("out", type=Path())
def run(data, out):
    """Run randomness tests on DATA."""
    try:
        series = parse_data(data)
        print_series(series)
    except (DataParsingError, NonBinarySequenceError) as e:
        print_error(e)
        exit(1)

    results = {}
    for name, result, e in run_all_tests(series):
        if not e:
            results[name] = result

    store_results(series, results, out)


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
@option(
    "-t",
    "--test",
    type=test_choice,
    help="Specify single test to run on data.",
    metavar="<test>",
)
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


@main.command()
@argument("results", type=Path(exists=True))
def read(results):
    report = load_results(results)
    print_series(report.series)
    console.print("")
    print_results(report.results)


@main.command()
@argument("results", type=Path(exists=True))
@argument("out", type=Path())
def report(results, out):
    report = load_results(results)
    write_report_doc(report, out)
