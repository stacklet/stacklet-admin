import io
import sys

import click

from cli.executor import _run_graphql
from cli.graphql import StackletGraphqlSnippet
from cli.utils import click_group_entry, default_options


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
    stacklet_snippet = StackletGraphqlSnippet(
        name="adhoc", snippet=snippet, variables=ctx.obj["page_variables"]
    )
    click.echo(
        _run_graphql(ctx=ctx, name=None, variables=None, snippet=stacklet_snippet)
    )
