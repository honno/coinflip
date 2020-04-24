import click

from prng.store import load as load_
from prng.store import manifest_keys


@click.group()
def main():
    pass


@main.command()
@click.argument("data", type=click.File("r"))
@click.argument("spec", type=click.File("r"))
@click.option("-o", "--overwrite", is_flag=True)
def load(data, spec, overwrite=False):
    load_(data, spec, overwrite)


@main.command()
def ls():
    for store_name in manifest_keys():
        click.echo(store_name)
