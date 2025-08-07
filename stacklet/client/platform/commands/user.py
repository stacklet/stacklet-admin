# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from stacklet.client.platform.cognito import CognitoUserManager
from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.utils import click_group_entry, default_options


@click.group(short_help="Run user queries/mutations")
@default_options()
@click.pass_context
def user(*args, **kwargs):
    """
    Execute User Operations
    """
    click_group_entry(*args, **kwargs)


@user.command()
@click.option("--username")
@click.option("--password", prompt="Password", confirmation_prompt=True, hide_input=True)  # noqa
@click.option("--email")
@click.option("--phone-number")
@click.option("--permanent/--not-permanent", default=True)
@click.pass_context
def add(ctx, username, password, email=None, phone_number=None, permanent=True):
    """
    Add a cognito user in Stacklet
    """
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        manager = CognitoUserManager.from_context(context)
        manager.create_user(
            user=username,
            password=password,
            email=email,
            phone_number=phone_number,
            permanent=permanent,
        )


@user.command("ensure-group")
@click.option("--username", required=True, help="the user to add to the group")
@click.option("--group", required=True, help="the group to add the user to (if it exists)")
@click.pass_context
def ensure_group(ctx, username, group):
    """
    Ensure that the specified user has the group if the group is available.
    """
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        manager = CognitoUserManager.from_context(context)
        success = manager.ensure_group(
            user=username,
            group=group,
        )
        ctx.exit(0 if success else 1)
