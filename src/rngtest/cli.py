from click import Choice
from click import File
from click import Path
from click import argument
from click import echo
from click import group
from click import option

from rngtest.report import write_report
from rngtest.stattests import __all__ as stattests
from rngtest.store import TYPES_MAP
from rngtest.store import drop
from rngtest.store import get_data
from rngtest.store import load_data
from rngtest.store import load_result
from rngtest.store import ls_stores
from rngtest.store import open_results
from rngtest.store import parse_data
from rngtest.tests_runner import run_all_tests
from rngtest.tests_runner import run_test


def get_stores(ctx, args, incomplete):
    """Completition for store names"""
    stores = list(ls_stores())
    if incomplete is None:
        return stores
    else:
        for name in stores:
            if incomplete in name:
                yield name


dtype_choice = Choice(TYPES_MAP.keys())
test_choice = Choice(stattests)


@group()
def main():
    pass


@main.command()
@argument("data", type=File("r"))
@option("-n", "--name", type=str)
@option("-t", "--dtype", type=dtype_choice)
@option("-o", "--overwrite", is_flag=True)
def load(data, name=None, dtype=None, overwrite=False):
    load_data(data, name=name, dtypestr=dtype, overwrite=overwrite)


@main.command()
@argument("store", autocompletion=get_stores)
def rm(store):
    drop(store)


@main.command()
def clear():
    for store in ls_stores():
        drop(store)


@main.command()
def ls():
    for store in ls_stores():
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
        results = run_all_tests(series)

        for result in results:
            print(result)
            load_result(store, result)

    else:
        result = run_test(series, test)

        print(result)
        load_result(store, result)


@main.command()
@argument("store", autocompletion=get_stores)
@argument("outfile", type=Path())
def report(store, outfile):
    with open_results(store) as results_dict:
        results = results_dict.values()
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
@argument("datafile", type=Path(exists=True))
@option("-t", "--dtype", type=dtype_choice)
@option("-t", "--test", type=test_choice)
@option("-r", "--report", type=Path())
def local_run(datafile, dtype=None, test=None, report=None):
    df = parse_data(datafile)
    series = df.iloc[:, 0]

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
