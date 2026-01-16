# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import io
import sys

import click

from ..executor import _run_graphql
from ..graphql import AdHocSnippet


@click.group()
def graphql(*args, **kwargs):
    """
    Run arbitrary graphql snippets
    """


@graphql.command()
@click.option("--snippet", help="Graphql Query or Mutation", default=sys.stdin)
@click.pass_obj
def run(obj, snippet):
    if isinstance(snippet, io.IOBase):
        snippet = snippet.read()

    # snippet must be a subclass, not an instance, of StackletGraphqlSnippet.
    click.echo(_run_graphql(obj, snippet=_ad_hoc(snippet)))


def _ad_hoc(snippet):
    "In practice, this is the most convenient way to create the subclass."
    return type("AdHocSnippet", (AdHocSnippet,), {"snippet": snippet})
