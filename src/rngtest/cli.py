from shutil import get_terminal_size

import pandas as pd
from click import Choice
from click import File
from click import Path
from click import argument
from click import echo
from click import group
from click import option
from colorama import Style
from colorama import init

from rngtest import generators
from rngtest.report import write_report
from rngtest.stattests import __all__ as stattests
from rngtest.stattests._common import blocks
from rngtest.stattests._common import pretty_seq
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

__all__ = [
    "load",
    "rm",
    "clear",
    "ls",
    "cat",
    "run",
    "report",
    "example_run",
    "local_run",
]

init()


stattest_fnames = {
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
    stattest_fname = stattest_fnames[stattest_name]
    underline = "".join("=" for _ in range(len(stattest_fname)))

    header = "\n" + stattest_fname + "\n" + underline

    echo(header)
    echo(result)


def echo_series(series):
    size = get_terminal_size()
    cols = max(size.columns, 40)  # 80 / 2

    candidate = series.unique()[0]

    if len(series) <= cols:
        fseries = pretty_seq(series, candidate)
        echo(fseries)
    else:
        l_arrow = Style.DIM + "< " + Style.RESET_ALL
        r_arrow = Style.DIM + " >" + Style.RESET_ALL

        rows = list(blocks(series, blocksize=cols - 4, cutoff=False))

        frow_first = "  " + pretty_seq(rows[0], candidate) + r_arrow
        echo(frow_first)

        for row in rows[1:-1]:
            frow = l_arrow + pretty_seq(row, candidate) + r_arrow
            echo(frow)

        frow_last = l_arrow + pretty_seq(rows[-1], candidate) + Style.RESET_ALL
        echo(frow_last)


@group()
def main():
    pass


@main.command()
@argument("data", type=File("r"))
@option("-n", "--name", type=str)
@option("-t", "--dtype", type=dtype_choice)
@option("-o", "--overwrite", is_flag=True)
def load(data, name, dtype, overwrite):
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
    echo_series(series)


@main.command()
@argument("store", autocompletion=get_stores)
@option("-t", "--test", type=test_choice)
def run(store, test):
    series = get_data(store)

    if test is None:
        results = {}
        for stattest_name, result in run_all_tests(series):
            echo_result(stattest_name, result)
            results[stattest_name] = result
        store_results(store, results)
    else:
        result = run_test(series, test)
        echo_result(test, result)
        store_result(store, test, result)


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
@option("-t", "--test", type=test_choice)
def example_run(example, length, test):
    generator_func = getattr(generators, example)
    generator = generator_func()

    series = pd.Series(next(generator) for _ in range(length))
    series = series.infer_objects()

    echo_series(series)

    if test is None:
        for stattest_name, result in run_all_tests(series):
            echo_result(stattest_name, result)
    else:
        result = run_test(series, test)
        echo_result(test, result)


@main.command()
@argument("datafile", type=Path(exists=True))
@option("-t", "--dtype", type=dtype_choice)
@option("-t", "--test", type=test_choice)
def local_run(datafile, dtype=None, test=None):
    series = parse_data(datafile)

    if test is None:
        for stattest_name, result in run_all_tests(series):
            echo_result(stattest_name, result)
    else:
        result = run_test(series, test)
        echo_result(test, result)
