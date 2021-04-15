import json
import os

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup

from cli.cognito import CognitoUserManager
from cli.commands import commands
from cli.config import StackletConfig
from cli.context import StackletContext
from cli.formatter import Formatter
from cli.utils import click_group_entry, default_options


@click.group(
    cls=HelpColorsGroup, help_headers_color="yellow", help_options_color="green"
)
@default_options()
@click.pass_context
def cli(*args, **kwargs):
    """
    Stacklet CLI

    Run graphql queries against Stacklet API. To get started run the following command
    and follow prompts to configure your Stacklet CLI:

        $ stacklet admin configure

    If this is your first time using Stacklet, create a user:

        $ stacklet admin create-user

    Now login:

        $ stacklet user login

    Your configuration file is saved to the directory: ~/.stacklet/config.json and your credentials
    are stored at ~/.stacklet/credentials. You may need to periodically login to refresh your
    authorization token.

    Run your first query:

        $ stacklet account list --provider AWS

    To specify a different configuration file or different API endpoint/Cognito Configuration:

    \b
        $ stacklet user \\
            --api $stacklet_api \\
            --cognito-client-id $cognito_client_id \\
            --cognito-user-pool-id $cognito_user_pool_id \\
            --region $region \\
            login

    or:

    \b
        $ stacklet user \\
            --config $config_file_location \\
            login

    Specify different output types:

        $ stacklet account --output json list --provider AWS

    Stacklet queries default to 20 entries per page. To use pagiantion:

    \b
        $ stacklet account \\
            --first 20 \\
            --last 20 \\
            --before $before_token \\
            --after $after_token \\
            list

    You can also use Stacklet CLI to run Cloud Custodian commands:

    \b
        $ stacklet custodian -h
    """
    click_group_entry(*args, **kwargs)


@cli.command(
    cls=HelpColorsCommand, help_headers_color="yellow", help_options_color="green"
)
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


@cli.command(
    cls=HelpColorsCommand, help_headers_color="yellow", help_options_color="green"
)
@click.option("--username")
@click.option(
    "--password", prompt="Password", confirmation_prompt=True, hide_input=True
)  # noqa
@click.option("--email")
@click.option("--phone-number")
@click.pass_context
def create_user(ctx, username, password, email, phone_number):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        manager = CognitoUserManager.from_context(context)
        manager.create_user(
            user=username, password=password, email=email, phone_number=phone_number
        )


@cli.command(
    cls=HelpColorsCommand, help_headers_color="yellow", help_options_color="green"
)
@click.pass_context
def show(ctx):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        fmt = Formatter.registry.get(ctx.obj["output"])()
        click.echo(fmt(context.config.to_json()))


@cli.command(
    cls=HelpColorsCommand, help_headers_color="yellow", help_options_color="green"
)
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


for c in commands:
    cli.add_command(c)


if __name__ == "__main__":
    cli()
