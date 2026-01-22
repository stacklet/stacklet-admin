# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import click
import jwt
import requests

from .cognito import CognitoUserManager
from .commands import commands
from .config import DEFAULT_CONFIG_FILE, DEFAULT_OUTPUT_FORMAT, StackletConfig
from .context import StackletContext
from .formatter import Formatter
from .utils import expand_user_path, setup_logging


@click.group()
@click.option(
    "--config",
    type=click.Path(path_type=Path, dir_okay=False),
    default=DEFAULT_CONFIG_FILE,
    envvar="STACKLET_CONFIG",
    show_envvar=True,
    callback=expand_user_path,
    help="Configuration file",
)
@click.option(
    "--output",
    type=click.Choice(list(Formatter.registry.keys()), case_sensitive=False),
    default=DEFAULT_OUTPUT_FORMAT,
    envvar="STACKLET_OUTPUT",
    show_envvar=True,
    help="Output type",
)
@click.option(
    "-v",
    count=True,
    default=0,
    help="Verbosity level, increase verbosity by appending v, e.g. -vvv",
)
@click.pass_context
def cli(
    ctx,
    config,
    output,
    v,
):
    """
    Stacklet CLI

    Run graphql queries against Stacklet API. To get started run the following command
    and follow prompts to configure your Stacklet CLI:

        $ stacklet-admin configure

    or specify the configuration parameters directly:

    \b
        $ stacklet-admin \\
            configure \\
            --api $stacklet_api \\
            --cognito-client-id $cognito_client_id \\
            --cognito-user-pool-id $cognito_user_pool_id \\
            --region $region
     \b

    In alternative, autoconfiguration can be used by specifying the deployment URL:

        $ stacklet-admin auto-configure --url https://console.myorg.stacklet.io

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
            --config $config_file_location \\
            login
    \b

    Specify different output types:

        $ stacklet-admin --output json account list --provider AWS

    Stacklet queries default to 20 entries per page. To use pagiantion:

    \b
        $ stacklet-admin account \\
            --first 20 \\
            --last 20 \\
            --before $before_token \\
            --after $after_token \\
            list
    \b
    """
    setup_logging(v)
    ctx.obj = StackletContext(config_file=config, output_format=output)


@cli.command(short_help="Configure stacklet-admin cli")
@click.option("--api", prompt="Stacklet API endpoint", help="Stacklet API endpoint")
@click.option("--region", prompt="Cognito Region", help="Cognito Region")
@click.option(
    "--cognito-client-id", prompt="Cognito User Pool Client ID", help="Cognito User Pool Client ID"
)
@click.option("--cognito-user-pool-id", prompt="Cognito User Pool ID", help="Cognito User Pool ID")
@click.option("--cubejs", prompt="Stacklet cube.js endpoint", help="Stacklet cube.js endpoint")
@click.option("--idp-id", prompt="(SSO) IDP ID", default="", help="(SSO) IDP ID")
@click.option("--auth-url", prompt="(SSO) Auth Url", default="", help="(SSO) Auth Url")
@click.option(
    "--location",
    type=click.Path(path_type=Path, dir_okay=False),
    default=DEFAULT_CONFIG_FILE,
    prompt="Config File Location",
    callback=expand_user_path,
    help="Config File Location",
)
def configure(
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
    config = StackletConfig.from_dict(
        {
            "api": api,
            "region": region,
            "cognito_client_id": cognito_client_id,
            "cognito_user_pool_id": cognito_user_pool_id,
            "idp_id": idp_id,
            "auth_url": auth_url,
            "cubejs": cubejs,
        }
    )
    config.to_file(location)
    click.echo(f"Saved config to {location}")


@cli.command()
@click.option(
    "--url",
    help="A Stacklet console URL",
)
@click.option(
    "--prefix",
    help="A deployment prefix (assumes hosting at .stacklet.io)",
)
@click.option(
    "--idp",
    help="Name of the Identity Provider to use for authentication, if more than one is available",
)
@click.option(
    "--location",
    default=str(DEFAULT_CONFIG_FILE),
    type=click.Path(path_type=Path, dir_okay=False),
    show_default=True,
    callback=expand_user_path,
)
def auto_configure(url, prefix, idp, location):
    """Automatically configure the stacklet-admin CLI

    Fetch configuration details from a live Stacklet instance and use it
    to populate a configuration file. Point to a Stacklet instance by
    name or deployment prefix.

    Examples:

    \b
    # Using a complete console URL
    > stacklet-admin auto-configure --url https://console.myorg.stacklet.io

    \b
    # Using a base domain
    > stacklet-admin auto-configure --url myorg.stacklet.io

    \b
    # Using a deployment prefix (assumes hosting at .stacklet.io)
    > stacklet-admin auto-configure --prefix myorg
    """
    # Validate mutual exclusion
    if url and prefix:
        raise click.ClickException(
            "Cannot specify both --url and --prefix. Please provide one or the other."
        )

    if not url and not prefix:
        raise click.ClickException("Must specify either --url or --prefix.")

    # Determine the host based on input type
    if prefix:
        # Handle prefix: always generate .stacklet.io URL
        host = f"console.{prefix}.stacklet.io"
        scheme = "https"
    else:
        # Handle URL: parse and potentially add console prefix
        parts = urlsplit(url, scheme="https", allow_fragments=False)
        host = parts.netloc or parts.path
        scheme = parts.scheme

        if not host.startswith("console"):
            # Be forgiving if we get a base URL like customer.stacklet.io
            host = f"console.{host}"

    config = {}
    try:
        for config_path in ("config/cognito.json", "config/cubejs.json"):
            config_url = urlunsplit(
                (
                    scheme,
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
        raise click.ClickException(f"Unable to connect to {config_url}\n{err}")
    except requests.exceptions.HTTPError as err:
        raise click.ClickException(
            f"Unable to retrieve configuration details from {config_url}\n{err}"
        )
    except requests.exceptions.JSONDecodeError as err:
        raise click.ClickException(
            f"Unable to parse configuration details from {config_url}\n{err}"
        )

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

        name_to_id: dict[str, str] = {}
        if saml_providers := config.get("saml_providers"):
            name_to_id = {p["name"]: p["idp_id"] for p in saml_providers}
        elif saml := config.get("saml"):
            # XXX legacy key, should be removed once the new one is everywhere
            name_to_id = {name: idp_id for idp_id, name in saml.items()}
        if len(name_to_id) == 0:
            # No SAML providers configured
            idp_id = ""
        elif len(name_to_id) == 1:
            _, idp_id = name_to_id.popitem()
        else:
            if not idp:
                raise click.ClickException(
                    "Multiple identity providers available, specify one with --idp: "
                    + ", ".join(sorted(name_to_id))
                )
            idp_id = name_to_id.get(idp)
            if not idp_id:
                raise click.ClickException(
                    f"Unknown identity provider '{idp}', known names: "
                    + ", ".join(sorted(name_to_id))
                )
        formatted_config["idp_id"] = idp_id
    except KeyError as err:
        raise click.ClickException(f"The configuration details are missing a required key: {err}")

    config = StackletConfig.from_dict(formatted_config)
    config.to_file(location)
    click.echo(f"Saved config to {location}")


@cli.command()
@click.pass_obj
def show(obj):
    """
    Show your config
    """
    fmt = obj.formatter()
    if id_token := obj.credentials.id_token():
        id_details = jwt.decode(id_token, options={"verify_signature": False})
        click.echo(fmt(id_details))
        click.echo()
    click.echo(fmt(obj.config.to_dict()))


@cli.command(short_help="Login to Stacklet")
@click.option("--username", help="Login username", required=False)
@click.option("--password", help="Login password", hide_input=True, required=False)
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
    context = ctx.obj
    config = context.config
    can_sso_login = bool(config.auth_url)
    # sso login
    if can_sso_login and not any([username, password]):
        from .vendored.auth import BrowserAuthenticator

        BrowserAuthenticator(
            authority_url=config.auth_url,
            client_id=config.cognito_client_id,
            idp_id=config.idp_id,
        )()
        return
    elif not can_sso_login and not any([username, password]):
        click.echo(
            "To login with SSO ensure that your configuration includes "
            + "auth_url, and cognito_client_id values."
        )
        ctx.exit(1)

    # handle login with username/password
    if not username:
        username = click.prompt("Username")
    if not password:
        password = click.prompt("Password", hide_input=True)
    manager = CognitoUserManager.from_context(context)
    id_token, access_token = manager.login(
        user=username,
        password=password,
    )
    context.credentials.write(id_token, access_token)


for c in commands:
    cli.add_command(c)


if __name__ == "__main__":
    cli()
