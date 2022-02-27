import io
import sys

import click

from ..executor import _run_graphql
from ..graphql import StackletGraphqlSnippet
from ..utils import click_group_entry, default_options


@click.group()
@default_options()
@click.pass_context
def graphql(*args, **kwargs):
    """
    Run arbitrary graphql snippets
    """
    click_group_entry(*args, **kwargs)


@graphql.command()
@click.option("--snippet", help="Graphql Query or Mutation", default=sys.stdin)
@click.pass_context
def run(ctx, snippet):
    if isinstance(snippet, io.IOBase):
        snippet = snippet.read()

    # snippet must be a subclass, not an instance, of StackletGraphqlSnippet.
    click.echo(_run_graphql(ctx=ctx, snippet=_ad_hoc(snippet)))


def _ad_hoc(snippet):
    "In practice, this is the most convenient way to create the subclass."
    return type("AdHocSnippet", (StackletGraphqlSnippet,), {"snippet": snippet})