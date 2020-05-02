import click

import prng.store as store_
from prng.runner import run_tests

store_choice = click.Choice(store_.ls_stores())
dtype_choice = click.Choice(store_.TYPES_MAP.keys())


@click.group()
def main():
    pass


@main.command()
@click.argument("data", type=click.File("r"))
@click.option("-n", "--name", type=str)
@click.option("-t", "--dtype", type=dtype_choice)
@click.option("-o", "--overwrite", is_flag=True)
def load(data, name=None, dtype=None, overwrite=False):
    store_.load(data, name=name, dtype_str=dtype, overwrite=overwrite)


profiles_prompt = """Profiles will be evaluated as Python code!
This is considered very unsafe. Do you wish to continue?"""


@main.command()
@click.argument("data", type=click.File("r"))
@click.argument("profiles", type=click.Path(exists=True))
@click.confirmation_option(prompt=profiles_prompt)
@click.option("-n", "--name", type=str)
@click.option("-t", "--dtype", type=dtype_choice)
@click.option("-o", "--overwrite", is_flag=True)
def profiles_load(data, profiles, name=None, dtype=None, overwrite=False):
    store_.load_with_profiles(data, profiles, name=name, dtype_str=dtype, overwrite=overwrite)


@main.command()
@click.argument("store", type=store_choice)
def rm(store):
    store_.drop(store)


@main.command()
def clear():
    for store in store_.ls_stores():
        store_.drop(store)


@main.command()
def ls():
    for store in store_.ls_stores():
        click.echo(store)


@main.command()
@click.argument("store", type=store_choice)
def cat(store):
    try:
        series = store_.get_single_profiled_data(store)
        click.echo(series)
    except store_.NotSingleProfiledError:
        for series in store_.get_profiled_data(store):
            click.echo(series)


@main.command()
@click.argument("store", type=store_choice)
def run(store):
    try:
        series = store_.get_single_profiled_data(store)
        run_tests(series)
    except store_.NotSingleProfiledError:
        for series in store_.get_profiled_data(store):
            run_tests(series)


@main.command()
@click.argument("datafile", type=click.File("r"))
@click.option("-t", "--dtype", type=dtype_choice)
def local_run(datafile, dtype=None):
    df = store_.parse_data(datafile)
    series = df.iloc[:, 0]
    run_tests(series)
