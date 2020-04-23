import click


@click.group()
def main():
    pass


@main.command()
@click.argument('data', type=click.File('r'))
@click.argument('spec', type=click.File('r'))
@click.option('-o', '--overwrite', is_flag=True)
def serialize(data, spec, overwrite=False):
    click.echo(spec.read())


@main.command()
def ls():
    pass
