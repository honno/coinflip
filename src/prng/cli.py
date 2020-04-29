import click

import prng.store as store
from prng.runner import run_tests


@click.group()
def main():
    pass


@main.command()
@click.argument("data", type=click.File("r"))
@click.argument("spec", type=click.File("r"))
@click.option("-o", "--overwrite", is_flag=True)
def load(data, spec, overwrite=False):
    store.load(data, spec, overwrite)


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
    with store.open_data(store_name) as df:
        click.echo(df)


@main.command()
@click.argument("store_name", type=str)
def run(store_name):
    for series in store.get_profiled_data(store_name):
        run_tests(series)


@main.command()
@click.argument("datafile", type=click.File("r"))
@click.argument("specfile", type=click.File("r"))
def local_run(datafile, specfile):
    df, spec = store.parse(datafile, specfile)
    profiles = store.spec2profiles(spec)

    for profile in profiles:
        series = store.profile_df(profile, df)
        run_tests(series)
