import json
import os

import click

from cli.cognito import CognitoUserManager
from cli.config import StackletConfig
from cli.context import StackletContext
from cli.formatter import Formatter
from cli.utils import click_group_entry, default_options


@click.group()
@default_options()
@click.pass_context
def admin(*args, **kwargs):
    """
    Run administrative actions against Stacklet
    """
    click_group_entry(*args, **kwargs)


@admin.command()
@click.option("--api", prompt="Stacklet API endpoint")
@click.option("--region", prompt="Cognito Region")
@click.option("--cognito-client-id", prompt="Cognito User Pool Client ID")
@click.option("--cognito-user-pool-id", prompt="Cognito User Pool ID")
@click.option(
    "--location", prompt="Config File Location", default="~/.stacklet/config.json"
)  # noqa
@click.pass_context
def configure(
    ctx,
    api,
    region,
    cognito_client_id,
    cognito_user_pool_id,
    location,
):
    """
    Interactively save a Stacklet Config file
    """
    config = {
        "api": api,
        "region": region,
        "cognito_client_id": cognito_client_id,
        "cognito_user_pool_id": cognito_user_pool_id,
    }

    StackletConfig.validate(config)

    if not os.path.exists(location):
        dirs = location.rsplit("/", 1)[0]
        os.makedirs(os.path.expanduser(dirs), exist_ok=True)

    with open(os.path.expanduser(location), "w+") as f:
        f.write(json.dumps(config))
    click.echo(f"Saved config to {location}")


@admin.command()
@click.option("--username", prompt="Username")
@click.option(
    "--password", prompt="Password", confirmation_prompt=True, hide_input=True
)  # noqa
@click.option("--email", prompt="Email")
@click.option("--phone-number", prompt="Phone Number")
@click.pass_context
def create_user(ctx, username, password, email, phone_number):
    """
    Create a user for use with Stacklet.
    """
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        manager = CognitoUserManager.from_context(context)
        manager.create_user(
            user=username, password=password, email=email, phone_number=phone_number
        )


@admin.command()
@click.pass_context
def show(ctx):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        fmt = Formatter.registry.get(ctx.obj["output"])()
        click.echo(fmt(context.config.to_json()))
