import webbrowser
from datetime import datetime
from pathlib import Path

import pandas as pd
from click import Choice
from click import Path as Path_
from click import argument
from click import group
from click import option
from rich.text import Text

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
    Informational web documents explaining the test results can be produced via
    the report command.
    """


@main.command()
@argument("data", type=Path_(exists=True))
@argument("out", type=Path_(), required=False, metavar="OUT")
@option(
    "-b",
    "--binary",
    is_flag=True,
    flag_value=True,
    help="Read DATA as a raw binary file.",
)
def run(data, out, binary):
    """Run randomness tests on DATA and write results to OUT.

    DATA is a newline-delimited text file which contains output of a random
    number generator.

    Individual results of each test are printed as they come. Once they are
    all finished, the results are written to OUT.

    The results saved in OUT can be printed again via the read command. OUT can
    also be used to generate an informational web document via the report
    command.
    """
    if not binary:
        try:
            series = parse_text(data)
        except (DataParsingError, NonBinarySequenceError) as e:
            print_error(e)
            exit(1)

    else:
        series = parse_binary(data)

    print_series(series)

    results = {}
    for name, result, e in run_all_tests(series):
        if not e:
            results[name] = result

    if out:
        path = Path(out)
        # TODO check if not pickle at end
    else:
        timestamp = datetime.now()
        f_timestamp = timestamp.strftime("%b%d_%H%M%S")
        path = Path(f"results_{f_timestamp}.pickle")

    store_results(series, results, path)

    if not out:
        console.print("")
        console.print(f"Results saved to {path}")


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
    """Run randomness tests on automatically generated data."""
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
@argument("results", type=Path_(exists=True))
def read(results):
    """Print test results."""
    report = load_results(results)
    print_series(report.series)
    console.print("")
    print_results(report.results)


@main.command()
@argument("results", type=Path_(exists=True))
@argument("out", type=Path_(), required=False, metavar="OUT")
def report(results, out):
    """Generate an informational web document from results."""
    report = load_results(results)

    if out:
        path = Path(out)
        # TODO check if not html at end
    else:
        timestamp = datetime.now()
        f_timestamp = timestamp.strftime("%b%d_%H%M%S")
        path = Path(f"report_{f_timestamp}.html")

    write_report_doc(report, path)

    if not out:
        console.print(f"Report saved to {path}")

    abs_path = path.absolute()
    url = abs_path.as_uri()
    url_msg = Text.assemble("View report at ", (str(abs_path), f"link {url}"))

    console.print(url_msg)
    webbrowser.open(url)
