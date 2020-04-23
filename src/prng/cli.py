import click


@click.command()
@click.argument('names', nargs=-1)
def main(names):
    click.echo(repr(names))
