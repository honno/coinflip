import click

import prng.store as store
from prng.runner import run_tests


@click.group()
def main():
    pass


@main.command()
@click.argument("data", type=click.File("r"))
@click.option("-n", "--name", type=str)
@click.option("-t", "--dtype", type=str)
@click.option("-o", "--overwrite", is_flag=True)
def load(data, name=None, dtype=None, overwrite=False):
    store.load(data, name=name, dtype_str=dtype, overwrite=overwrite)


profiles_prompt = """Profiles will be evaluated as Python code!
This is considered very unsafe. Do you wish to continue?"""


@main.command()
@click.argument("data", type=click.File("r"))
@click.argument("profiles", type=click.Path(exists=True))
@click.confirmation_option(prompt=profiles_prompt)
@click.option("-n", "--name", type=str)
@click.option("-t", "--dtype", type=str)
@click.option("-o", "--overwrite", is_flag=True)
def profiles_load(data, profiles, name=None, dtype=None, overwrite=False):
    store.load_with_profiles(data, profiles, name=name, dtype_str=dtype, overwrite=overwrite)


@main.command()
@click.argument("store_name", type=str)
def rm(store_name):
    store.drop(store_name)


@main.command()
def clear():
    for store_name in store.ls_stores():
        store.drop(store_name)


@main.command()
def ls():
    for store_name in store.ls_stores():
        click.echo(store_name)


@main.command()
@click.argument("store_name", type=str)
def cat(store_name):
    try:
        series = store.get_single_profiled_data(store_name)
        click.echo(series)
    except store.NotSingleProfiledError:
        for series in store.get_profiled_data(store_name):
            click.echo(series)


@main.command()
@click.argument("store_name", type=str)
def run(store_name):
    try:
        series = store.get_single_profiled_data(store_name)
        run_tests(series)
    except store.NotSingleProfiledError:
        for series in store.get_profiled_data(store_name):
            run_tests(series)


@main.command()
@click.argument("datafile", type=click.File("r"))
@click.option("-t", "--dtype", type=str)
def local_run(datafile, dtype=None):
    df = store.parse_data(datafile)
    series = df.iloc[0]
    run_tests(series)
