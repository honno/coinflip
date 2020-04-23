import click

READ_FILE_TYPE = click.File(mode='r', encoding='utf-8')


@click.group()
def main():
    pass


@main.command()
@click.argument('data', type=READ_FILE_TYPE)
@click.argument('spec', type=READ_FILE_TYPE)
@click.option('-o', '--overwrite', is_flag=True)
def serialize(data, spec, overwrite=False):
    pass


@main.command()
def ls():
    pass
