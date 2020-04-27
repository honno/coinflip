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
def ls():
    for store_name in store.manifest_keys():
        click.echo(store_name)


@main.command()
@click.argument("store_name", type=str)
def cat(store_name):
    with store.open_data(store_name) as df:
        click.echo(df)


@main.command()
@click.argument("store_name", type=str)
def run(store_name):
    with store.open_data(store_name) as df:
        run_tests(df)


@main.command()
@click.argument("data", type=click.File("r"))
@click.argument("spec", type=click.File("r"))
def local_run(data, spec):
    df, spec = store.prepare(data, spec)

    run_tests(df)
