import click

from cli.commands.accounts import accounts
from cli.commands.admin import admin


@click.group()
def cli():
    """
    Stacklet CLI
    """
    pass


cli.add_command(admin)
cli.add_command(accounts)


if __name__ == "__main__":
    cli()
