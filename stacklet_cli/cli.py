import json
import os

import click

from stacklet_cli.cognito import CognitoUserManager
from stacklet_cli.commands import commands
from stacklet_cli.config import StackletConfig
from stacklet_cli.context import StackletContext
from stacklet_cli.formatter import Formatter
from stacklet_cli.utils import click_group_entry, default_options


@click.group()
@default_options()
@click.pass_context
def cli(*args, **kwargs):
    """
    Stacklet CLI

    Run graphql queries against Stacklet API. To get started run the following command
    and follow prompts to configure your Stacklet CLI:

        $ stacklet-admin configure

    If this is your first time using Stacklet, create a user:

        $ stacklet-admin create-user

    Now login:

        $ stacklet-admin login

    Your configuration file is saved to the directory: ~/.stacklet/config.json and your credentials
    are stored at ~/.stacklet/credentials. You may need to periodically login to refresh your
    authorization token.

    Run your first query:

        $ stacklet-admin account list --provider AWS

    To specify a different configuration file or different API endpoint/Cognito Configuration:

    \b
        $ stacklet-admin \\
            --api $stacklet_api \\
            --cognito-client-id $cognito_client_id \\
            --cognito-user-pool-id $cognito_user_pool_id \\
            --region $region \\
            login

    or:

    \b
        $ stacklet-admin \\
            --config $config_file_location \\
            login

    Specify different output types:

        $ stacklet-admin account --output json list --provider AWS

    Stacklet queries default to 20 entries per page. To use pagiantion:

    \b
        $ stacklet-admin account \\
            --first 20 \\
            --last 20 \\
            --before $before_token \\
            --after $after_token \\
            list
    """
    click_group_entry(*args, **kwargs)


@cli.command()
@click.option("--api", prompt="Stacklet API endpoint")
@click.option("--region", prompt="Cognito Region")
@click.option("--cognito-client-id", prompt="Cognito User Pool Client ID")
@click.option("--cognito-user-pool-id", prompt="Cognito User Pool ID")
@click.option("--idp-id", prompt="(SSO) IDP ID")
@click.option("--auth-url", prompt="(SSO) Auth Url")
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
    idp_id,
    auth_url,
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
        "idp_id": idp_id,
        "auth_url": auth_url,
    }

    StackletConfig.validate(config)

    if not os.path.exists(location):
        dirs = location.rsplit("/", 1)[0]
        os.makedirs(os.path.expanduser(dirs), exist_ok=True)

    with open(os.path.expanduser(location), "w+") as f:
        f.write(json.dumps(config))
    click.echo(f"Saved config to {location}")


@cli.command()
@click.option("--username")
@click.option(
    "--password", prompt="Password", confirmation_prompt=True, hide_input=True
)  # noqa
@click.option("--email")
@click.option("--phone-number")
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


@cli.command()
@click.pass_context
def show(ctx):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        fmt = Formatter.registry.get(ctx.obj["output"])()
        click.echo(fmt(context.config.to_json()))


@cli.command()
@click.option("--username", required=False)
@click.option("--password", hide_input=True, required=False)
@click.pass_context
def login(ctx, username, password):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        # sso login
        if context.can_sso_login() and not any([username, password]):
            from stacklet_cli.vendored.auth import _get_authorization_code_worker

            _get_authorization_code_worker(
                authority_url=context.config.auth_url,
                client_id=context.config.cognito_client_id,
                idp_id=context.config.idp_id,
            )
            return
        elif not context.can_sso_login() and not any([username, password]):
            click.echo(
                "To login with SSO ensure that your configuration includes "
                + "auth_url, and cognito_client_id values."
            )
            raise Exception()

        # handle login with username/password
        if not username:
            password = click.prompt("Username")
        if not password:
            password = click.prompt("Password", hide_input=True)
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
