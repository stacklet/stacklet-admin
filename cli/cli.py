import click

from cli.commands import commands


@click.group()
def cli():
    """
    Stacklet CLI
    """
    pass


for c in commands:
    cli.add_command(c)


if __name__ == "__main__":
    cli()
