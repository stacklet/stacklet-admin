import os

import click

from cli.cognito import CognitoUserManager
from cli.context import StackletContext
from cli.utils import click_group_entry, default_options


@click.group()
@default_options()
@click.pass_context
def user(*args, **kwargs):
    """
    Execute User Operations
    """
    click_group_entry(*args, **kwargs)


@user.command()
@click.option("--username", prompt="Username")
@click.option("--password", prompt="Password", hide_input=True)
@click.pass_context
def login(ctx, username, password):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
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
