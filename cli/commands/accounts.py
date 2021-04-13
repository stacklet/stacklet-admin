import click

from cli.context import StackletContext
from cli.formatter import Formatter
from cli.fragments import _run_fragment, fragment_options


@click.group()
@click.option("--config", default=StackletContext.DEFAULT_CONFIG)
@click.option(
    "--output",
    type=click.Choice(list(Formatter.registry.keys()), case_sensitive=False),
    default=StackletContext.DEFAULT_OUTPUT,
)
@click.pass_context
def accounts(ctx, config, output):
    """
    Query against and Run mutations against Account objects in Stacklet.

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet accounts --output json list

    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["output"] = output


@accounts.command()
@fragment_options("list-accounts")
@click.pass_context
def list(ctx):
    click.echo(_run_fragment(ctx=ctx, name="list-accounts", variables=None))


@accounts.command()
@fragment_options("add-account")
@click.pass_context
def add_account(ctx, **kwargs):
    click.echo(_run_fragment(ctx=ctx, name="add-account", variables=dict(**kwargs)))
