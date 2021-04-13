import click
import os

from cli.formatter import Formatter
from cli.cognito import CognitoUserManager
from cli.context import StackletContext


@click.group()
@click.option("--config", default=StackletContext.DEFAULT_CONFIG)
@click.option(
    "--output",
    type=click.Choice(list(Formatter.registry.keys()), case_sensitive=False),
    default=StackletContext.DEFAULT_OUTPUT,
)
@click.pass_context
def user(ctx, config, output):
    """
    Execute User Operations
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["output"] = output


@user.command()
@click.option("--username", prompt="Username")
@click.option("--password", prompt="Password", hide_input=True)
@click.pass_context
def login(ctx, username, password):
    with StackletContext(ctx.obj["config"]) as context:
        if username == "" and context.config.username is None:
            raise Exception("No username specified")
        manager = CognitoUserManager.from_context(context)
        res = manager.login(
            user=username,
            password=password,
        )
        with open(
            os.path.expanduser(StackletContext.DEFAULT_CREDENTIALS), "w+"
        ) as f:  # noqa
            f.write(res)
