from click import Choice
from click import File
from click import Path
from click import argument
from click import confirmation_option
from click import echo
from click import group
from click import option

import rngtest.store as store_
import rngtest.tests_runner as runner


def get_stores(ctx, args, incomplete):
    """Completition for store names"""
    stores = list(store_.ls_stores())
    if incomplete is None:
        return stores
    else:
        for name in stores:
            if incomplete in name:
                yield name


dtype_choice = Choice(store_.TYPES_MAP.keys())
test_choice = Choice(runner.list_tests())


@group()
def main():
    pass


@main.command()
@argument("data", type=File("r"))
@option("-n", "--name", type=str)
@option("-t", "--dtype", type=dtype_choice)
@option("-o", "--overwrite", is_flag=True)
def load(data, name=None, dtype=None, overwrite=False):
    store_.load(data, name=name, dtype_str=dtype, overwrite=overwrite)


profiles_prompt = """Profiles will be evaluated as Python code!
This is considered very unsafe. Do you wish to continue?"""


@main.command()
@argument("data", type=File("r"))
@argument("profiles", type=Path(exists=True))
@confirmation_option(prompt=profiles_prompt)
@option("-n", "--name", type=str)
@option("-t", "--dtype", type=dtype_choice)
@option("-o", "--overwrite", is_flag=True)
def profiles_load(data, profiles, name=None, dtype=None, overwrite=False):
    store_.load_with_profiles(
        data, profiles, name=name, dtype_str=dtype, overwrite=overwrite
    )


@main.command()
@argument("store", autocompletion=get_stores)
def rm(store):
    store_.drop(store)


@main.command()
def clear():
    for store in store_.ls_stores():
        store_.drop(store)


@main.command()
def ls():
    for store in store_.ls_stores():
        echo(store)


@main.command()
@argument("store", autocompletion=get_stores)
def cat(store):
    try:
        series = store_.get_single_profiled_data(store)
        echo(series)
    except store_.NotSingleProfiledError:
        for series in store_.get_profiled_data(store):
            echo(series)


@main.command()
@argument("store", autocompletion=get_stores)
@option("-t", "--test", type=test_choice)
def run(store, test=None):
    try:
        series = store_.get_single_profiled_data(store)
        profiles = [series]
    except store_.NotSingleProfiledError:
        profiles = store_.get_profiled_data(store)

    for profile in profiles:
        if test is None:
            runner.run_all_tests(series)
        else:
            runner.run_test(series, test)


@main.command()
@argument("datafile", type=Path(exists=True))
@option("-t", "--dtype", type=dtype_choice)
@option("-t", "--test", type=test_choice)
@option("-r", "--report", type=Path())
def local_run(datafile, dtype=None, test=None, report=None):
    df = store_.parse_data(datafile)
    series = df.iloc[:, 0]

    if test is None:
        results = runner.run_all_tests(series)
    else:
        result = runner.run_test(series, test)
        breakpoint()

        results = [result]

    if report:
        html = []
        for result in results:
            try:
                markup = result.report()
                html.append(markup)
            except NotImplementedError:
                echo(f"No report markup provided for {result.__class__}")

        if len(html) != 0:
            with open(report, "w") as f:
                f.writelines(html)
        else:
            echo("No report markup available!")
