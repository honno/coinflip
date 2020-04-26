import click

import prng.store as store


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
def ls():
    for store_name in store.manifest_keys():
        click.echo(store_name)


@main.command()
@click.argument("store_name", type=str)
def cat(store_name):
    with store.open_data(store_name) as data:
        for x in data:
            click.echo(x)
