from click import File
from click import argument
from click import echo
from click import group
from click import option

from prng.store import load as load_
from prng.store import manifest_keys
from prng.store import open_data


@group()
def main():
    pass


@main.command()
@argument("data", type=File("r"))
@argument("spec", type=File("r"))
@option("-o", "--overwrite", is_flag=True)
def load(data, spec, overwrite=False):
    load_(data, spec, overwrite)


@main.command()
def ls():
    for store_name in manifest_keys():
        echo(store_name)


@main.command()
@argument("store_name", type=str)
def cat(store_name):
    with open_data(store_name) as data:
        for x in data:
            echo(x)
