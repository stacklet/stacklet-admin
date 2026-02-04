# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import io
import sys

import click

from ..graphql.cli import run_graphql


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

    click.echo(run_graphql(obj, snippet=snippet))
