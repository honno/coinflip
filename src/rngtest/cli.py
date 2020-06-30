import warnings
from shutil import get_terminal_size

import pandas as pd
from click import Choice
from click import File
from click import Path
from click import argument
from click import echo
from click import group
from click import option
from colorama import Fore
from colorama import init

from rngtest import generators
from rngtest.report import write_report
from rngtest.stattests import __all__ as stattest_names
from rngtest.stattests._common import dim
from rngtest.stattests._common import pretty_seq
from rngtest.stattests._common.exceptions import NonBinarySequenceError
from rngtest.store import PARSE_EXCEPTION
from rngtest.store import STORE_EXCEPTION
from rngtest.store import TYPES
from rngtest.store import StoreNotFoundError
from rngtest.store import drop
from rngtest.store import get_data
from rngtest.store import list_stores
from rngtest.store import open_results
from rngtest.store import parse_data
from rngtest.store import store_data
from rngtest.store import store_result
from rngtest.store import store_results
from rngtest.tests_runner import TEST_EXCEPTION
from rngtest.tests_runner import run_all_tests
from rngtest.tests_runner import run_test

__all__ = [
    "load",
    "rm",
    "clear",
    "ls",
    "cat",
    "run",
    "example_run",
    "local_run",
    "report",
]

# ------------------------------------------------------------------------------
# Pretty printing


init()  # colorama's magical method for Windows compatibility

warn_txt = Fore.YELLOW + "WARN" + Fore.RESET
err_txt = Fore.RED + "ERR!" + Fore.RESET


def formatwarning(msg, *args, **kwargs):
    return dim(f"{warn_txt} {msg}\n")


warnings.formatwarning = formatwarning


def echo_err(error: Exception, final=True):
    line = f"{err_txt} {error}"
    if not final:
        line += "\n"

    echo(line)

    if final:
        exit(1)


def echo_series(series):
    size = get_terminal_size()
    cols = min(size.columns, 80)

    echo(pretty_seq(series, cols))


# ------------------------------------------------------------------------------
# Autocompletion


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
test_choice = Choice(stattest_names)

# ------------------------------------------------------------------------------
# Commands


@group()
def main():
    pass


@main.command()
@argument("data", type=File("r"))
@option("-n", "--name", type=str)
@option("-t", "--dtype", type=dtype_choice)
@option("-o", "--overwrite", is_flag=True)
def load(data, name, dtype, overwrite):
    try:
        store_data(data, name=name, dtype_str=dtype, overwrite=overwrite)
    except STORE_EXCEPTION as e:
        echo_err(e)


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
    try:
        series = get_data(store)
        echo_series(series)
    except StoreNotFoundError as e:
        echo_err(e)


# TODO save per result
@main.command()
@argument("store", autocompletion=get_stores)
@option("-t", "--test", type=test_choice)
def run(store, test):
    try:
        series = get_data(store)
    except StoreNotFoundError as e:
        echo_err(e)

    try:
        if not test:
            results = {}
            for name, result, e in run_all_tests(series):
                if e:
                    echo_err(e, final=False)
                else:
                    results[name] = result

            store_results(store, results)
            echo("Results stored!")
        else:
            try:
                result = run_test(series, test)
                store_result(store, test, result)
                echo("Result stored!")

            except TEST_EXCEPTION as e:
                echo_err(e)

    except NonBinarySequenceError as e:
        echo_err(e)


@main.command()
@option("-e", "--example", type=Choice(generators.__all__), default="python")
@option("-n", "--length", type=int, default=512)
@option("-t", "--test", type=test_choice)
def example_run(example, length, test):
    generator_func = getattr(generators, example)
    generator = generator_func()

    series = pd.Series(next(generator) for _ in range(length))
    series = series.infer_objects()
    echo_series(series)

    try:
        if not test:
            for name, result, e in run_all_tests(series):
                if e:
                    echo_err(e, final=False)

        else:
            try:
                run_test(series, test)
            except TEST_EXCEPTION as e:
                echo_err(e)

    except NonBinarySequenceError as e:
        echo_err(e)


@main.command()
@argument("datafile", type=Path(exists=True))
@option("-t", "--dtype", type=dtype_choice)
@option("-t", "--test", type=test_choice)
def local_run(datafile, dtype, test):
    try:
        series = parse_data(datafile)
        echo_series(series)
    except PARSE_EXCEPTION as e:
        echo_err(e)

    try:
        if not test:
            for name, result, e in run_all_tests(series):
                if e:
                    echo_err(e, final=False)

        else:
            try:
                run_test(series, test)
            except TEST_EXCEPTION as e:
                echo_err(e)

    except NonBinarySequenceError as e:
        echo_err(e)


@main.command()
@argument("store", autocompletion=get_stores)
@argument("outfile", type=Path())
def report(store, outfile):
    try:
        with open_results(store) as results:
            results = results.values()
            html = []
            for result in results:
                try:
                    markup = result.report()
                    html.append(markup)
                except NotImplementedError as e:
                    echo_err(e)

    except StoreNotFoundError as e:
        echo_err(e)

    if len(html) != 0:
        markup = "".join(html)
        write_report(markup, outfile)
    else:
        echo("No report markup available!")
