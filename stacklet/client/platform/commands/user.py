import click

from stacklet.client.platform.utils import click_group_entry, default_options
from stacklet.client.platform.cognito import CognitoUserManager
from stacklet.client.platform.context import StackletContext


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
@click.option(
    "--password", prompt="Password", confirmation_prompt=True, hide_input=True
)  # noqa
@click.option("--email")
@click.option("--phone-number")
@click.pass_context
def add(ctx, username, password, email=None, phone_number=None):
    """
    Add a cognito user in Stacklet
    """
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        manager = CognitoUserManager.from_context(context)
        manager.create_user(
            user=username, password=password, email=email, phone_number=phone_number
        )
