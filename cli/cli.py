import click

from cli.commands.account import account
from cli.commands.admin import admin
from cli.commands.repository import repository


@click.group()
def cli():
    """
    Stacklet CLI
    """
    pass


cli.add_command(admin)
cli.add_command(account)
cli.add_command(repository)


if __name__ == "__main__":
    cli()
