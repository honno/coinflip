import click

from prng.store import manifest_keys
from prng.store import store


@click.group()
def main():
    pass


@main.command()
@click.argument("data", type=click.File("r"))
@click.argument("spec", type=click.File("r"))
@click.option("-o", "--overwrite", is_flag=True)
def serialize(data, spec, overwrite=False):
    store(data, spec, overwrite)


@main.command()
def ls():
    for store_name in manifest_keys():
        click.echo(store_name)
