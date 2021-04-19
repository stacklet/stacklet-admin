import click

from stacklet_cli.utils import click_group_entry, default_options


@click.group()
@default_options()
@click.pass_context
def user(*args, **kwargs):
    """
    Execute User Operations
    """
    click_group_entry(*args, **kwargs)
