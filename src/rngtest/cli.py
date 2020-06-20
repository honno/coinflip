# TODO replace kwarg defaults with click defaults
import pandas as pd
from click import Choice
from click import File
from click import Path
from click import argument
from click import echo
from click import group
from click import option

from rngtest import generators
from rngtest.report import write_report
from rngtest.stattests import __all__ as stattests
from rngtest.store import TYPES
from rngtest.store import drop
from rngtest.store import get_data
from rngtest.store import list_stores
from rngtest.store import open_results
from rngtest.store import parse_data
from rngtest.store import store_data
from rngtest.store import store_result
from rngtest.store import store_results
from rngtest.tests_runner import run_all_tests
from rngtest.tests_runner import run_test


def get_stores(ctx, args, incomplete):
    """Completition for store names"""
    stores = list(list_stores())
    if incomplete is None:
        return stores
    else:
        for name in stores:
            if incomplete in name:
                yield name


dtype_choice = Choice(TYPES.keys())
test_choice = Choice(stattests)


def echo_result(stattest_name, result):
    underline = "".join("=" for _ in range(len(stattest_name)))
    header = "\n" + stattest_name + "\n" + underline
    echo(header)
    echo(result)


@group()
def main():
    pass


@main.command()
@argument("data", type=File("r"))
@option("-n", "--name", type=str)
@option("-t", "--dtype", type=dtype_choice)
@option("-o", "--overwrite", is_flag=True)
def load(data, name=None, dtype=None, overwrite=False):
    store_data(data, name=name, dtype_str=dtype, overwrite=overwrite)


@main.command()
@argument("store", autocompletion=get_stores)
def rm(store):
    drop(store)


@main.command()
def clear():
    for store in list_stores():
        drop(store)


@main.command()
def ls():
    for store in list_stores():
        echo(store)


@main.command()
@argument("store", autocompletion=get_stores)
def cat(store):
    series = get_data(store)
    echo(series)


@main.command()
@argument("store", autocompletion=get_stores)
@option("-t", "--test", type=test_choice)
def run(store, test=None):
    series = get_data(store)

    if test is None:
        results_dict = run_all_tests(series)
        store_results(store, results_dict)
    else:
        stattest_name, result = run_test(series, test)
        store_result(store, stattest_name, result)


@main.command()
@argument("store", autocompletion=get_stores)
@argument("outfile", type=Path())
def report(store, outfile):
    with open_results(store) as results:
        results = results.values()
        html = []
        for result in results:
            try:
                markup = result.report()
                html.append(markup)
            except NotImplementedError:
                echo(f"No report markup provided for {result.__class__.__name__}")

    if len(html) != 0:
        markup = "".join(html)
        write_report(markup, outfile)
    else:
        echo("No report markup available!")


@main.command()
@option("-e", "--example", type=Choice(generators.__all__), default="python")
@option("-n", "--length", type=int, default=256)
@option("-t", "--test", type=test_choice, default=None)
def example_run(example, length, test):
    generator_func = getattr(generators, example)
    generator = generator_func()

    series = pd.Series(next(generator) for _ in range(length))
    series = series.infer_objects()

    echo(series)

    if test is None:
        for stattest_name, result in run_all_tests(series):
            echo_result(stattest_name, result)
    else:
        stattest_name, result = run_test(series, test)
        echo_result(stattest_name, result)


# TODO update with new test runner functionality
@main.command()
@argument("datafile", type=Path(exists=True))
@option("-t", "--dtype", type=dtype_choice)
@option("-t", "--test", type=test_choice)
@option("-r", "--report", type=Path())
def local_run(datafile, dtype=None, test=None, report=None):
    series = parse_data(datafile)

    if test is None:
        results = run_all_tests(series)
    else:
        result = run_test(series, test)
        results = [result]

    if report:
        html = []
        for result in results:
            try:
                markup = result.report()
                html.append(markup)
            except NotImplementedError:
                echo(f"No report markup provided for {result.__class__.__name__}")

        if len(html) != 0:
            markup = "\n".join(html)
            write_report(markup, report)
        else:
            echo("No report markup available!")
