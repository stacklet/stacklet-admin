import json
import os
import pathlib

from urllib.parse import urlsplit, urlunsplit
import click
import jwt
import requests

from stacklet.client.platform.cognito import CognitoUserManager
from stacklet.client.platform.commands import commands
from stacklet.client.platform.config import StackletConfig
from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.formatter import Formatter
from stacklet.client.platform.utils import click_group_entry, default_options


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

        $ stacklet-admin user add

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


@cli.command(short_help="Configure stacklet-admin cli")
@click.option("--api", prompt="Stacklet API endpoint")
@click.option("--region", prompt="Cognito Region")
@click.option("--cognito-client-id", prompt="Cognito User Pool Client ID")
@click.option("--cognito-user-pool-id", prompt="Cognito User Pool ID")
@click.option("--idp-id", prompt="(SSO) IDP ID", default="")
@click.option("--auth-url", prompt="(SSO) Auth Url", default="")
@click.option("--cubejs", prompt="Stacklet cube.js endpoint", default="")
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
    cubejs,
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
        "cubejs": cubejs,
    }

    StackletConfig.validate(config)

    if not os.path.exists(location):
        dirs = location.rsplit("/", 1)[0]
        os.makedirs(os.path.expanduser(dirs), exist_ok=True)

    with open(os.path.expanduser(location), "w+") as f:
        f.write(json.dumps(config))
    click.echo(f"Saved config to {location}")


@cli.command(short_help="Automatically configure stacklet-admin cli")
@click.option("--prefix", "--url", required=True)
@click.option(
    "--location",
    default="~/.stacklet/config.json",
    type=click.Path(path_type=pathlib.Path, dir_okay=False),
)
@click.pass_context
def auto_configure(ctx, prefix, location):
    parts = urlsplit(prefix, scheme="https", allow_fragments=False)
    host = parts.netloc or parts.path

    if "." not in host:
        # Assume that we have a prefix for a Stacklet instance
        # hosted under stacklet.io
        host = f"console.{host}.stacklet.io"
    if not host.startswith("console"):
        # Be forgiving if we get a base URL like customer.stacklet.io
        host = f"console.{host}"

    config = {}
    try:
        for config_path in ("config/cognito.json", "config/cubejs.json"):
            config_url = urlunsplit(
                (
                    parts.scheme,
                    host,
                    config_path,
                    None,
                    None,
                )
            )
            response = requests.get(config_url)
            response.raise_for_status()
            config.update(response.json())
    except requests.exceptions.ConnectionError as err:
        click.echo(f"Unable to connect to {config_url}")
        click.echo(err)
        return
    except requests.exceptions.HTTPError as err:
        click.echo(f"Unable to retrieve configuration details from {config_url}")
        click.echo(err)
        return
    except requests.exceptions.JSONDecodeError as err:
        click.echo(f"Unable to parse configuration details from {config_url}")
        click.echo(err)
        return

    try:
        auth_url = f"https://{config['cognito_install']}"
        formatted_config = {
            "api": auth_url.replace("auth.console", "api"),
            "region": config["cognito_user_pool_region"],
            "cognito_user_pool_id": config["cognito_user_pool_id"],
            "cognito_client_id": config["cognito_user_pool_client_id"],
            "auth_url": auth_url,
            "cubejs": f"https://{config['cubejs_domain']}",
        }
        saml_config = config.get("saml")
        if saml_config:
            formatted_config["idp_id"], _ = saml_config.popitem()
    except KeyError as err:
        click.echo("The configuration details are missing a required key")
        click.echo(err)
        return

    config_file = location.expanduser()
    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)

    config_file.write_text(json.dumps(formatted_config, indent=4, sort_keys=True))

    click.echo(f"Saved config to {config_file}")


@cli.command()
@click.pass_context
def show(ctx):
    """
    Show your config
    """
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        fmt = Formatter.registry.get(ctx.obj["output"])()
        if os.path.exists(os.path.expanduser(StackletContext.DEFAULT_ID)):
            with open(os.path.expanduser(StackletContext.DEFAULT_ID), "r") as f:
                id_details = jwt.decode(f.read(), options={"verify_signature": False})
            click.echo(fmt(id_details))
            click.echo()
        click.echo(fmt(context.config.to_json()))


@cli.command(short_help="Login to Stacklet")
@click.option("--username", required=False)
@click.option("--password", hide_input=True, required=False)
@click.pass_context
def login(ctx, username, password):
    """
    Login to Stacklet

        $ stacklet-admin login

    Spawns a web browser to login via SSO or Cognito. To login with a Cognito user
    with username and password, simply pass those options into the CLI:

        $ stacklet-admin login --username my-user

    If password is not passed in, your password will be prompted
    """
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        # sso login
        if context.can_sso_login() and not any([username, password]):
            from stacklet.client.platform.vendored.auth import BrowserAuthenticator

            BrowserAuthenticator(
                authority_url=context.config.auth_url,
                client_id=context.config.cognito_client_id,
                idp_id=context.config.idp_id,
            )()
            return
        elif not context.can_sso_login() and not any([username, password]):
            click.echo(
                "To login with SSO ensure that your configuration includes "
                + "auth_url, and cognito_client_id values."
            )
            raise Exception()

        # handle login with username/password
        if not username:
            username = click.prompt("Username")
        if not password:
            password = click.prompt("Password", hide_input=True)
        manager = CognitoUserManager.from_context(context)
        res = manager.login(
            user=username,
            password=password,
        )
        if not os.path.exists(
            os.path.dirname(os.path.expanduser(StackletContext.DEFAULT_CREDENTIALS))
        ):
            os.makedirs(
                os.path.dirname(os.path.expanduser(StackletContext.DEFAULT_CREDENTIALS))
            )
        with open(
            os.path.expanduser(StackletContext.DEFAULT_CREDENTIALS), "w+"
        ) as f:  # noqa
            f.write(res)


for c in commands:
    cli.add_command(c)


if __name__ == "__main__":
    cli()
