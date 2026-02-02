# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Any, Callable

import click

from ..context import StackletContext
from ..utils import PAGINATION_OPTIONS, wrap_command
from .snippet import GraphQLSnippet


def snippet_options(snippet_class: type[GraphQLSnippet]):
    def wrapper(func):
        if not snippet_class:
            return func
        func = wrap_command(func, snippet_class.required, required=True)
        func = wrap_command(func, snippet_class.optional)
        if snippet_class.pagination_expr is not None:
            func = wrap_command(func, PAGINATION_OPTIONS)
        return func

    return wrapper


def run_graphql(
    context: StackletContext,
    snippet_class: type[GraphQLSnippet] | None = None,
    snippet: str | None = None,
    variables=None,
    raw=False,
):
    if snippet is not None:
        res = context.executor.run_query(snippet)
    else:
        res = context.executor.run_snippet(
            snippet_class, variables=variables, transform_variables=True
        )
    if raw:
        return res
    fmt = context.formatter()
    return fmt(res)


@dataclass
class GraphQLCommand:
    """A GraphQL-based CLI command."""

    name: str
    snippet_class: type[GraphQLSnippet]
    help: str
    # Check performed before calling the GraphQL snippet. It's called with the
    # context object and command line args and must return (possibly processed)
    # command line args, and raise errors case of failure.
    pre_check: Callable[[StackletContext, dict[str, Any]], dict[str, Any]] | None = None


def register_graphql_commands(group: click.Group, commands: list[GraphQLCommand]):
    """
    Register multiple GraphQL snippet commands at once.

    Args:
        group: Click group to add commands to
        commands: List of GraphQLCommand objects
    """
    for cmd in commands:
        group.add_command(_graphql_snippet_command(cmd))


def _graphql_snippet_command(cmd: GraphQLCommand):
    """Create a CLI command that runs a GraphQL snippet and prints out the result."""

    @snippet_options(cmd.snippet_class)
    @click.pass_obj
    def command(context: StackletContext, **cli_args):
        if cmd.pre_check:
            cli_args = cmd.pre_check(context, cli_args)

        click.echo(run_graphql(context, snippet_class=cmd.snippet_class, variables=cli_args))

    return click.command(name=cmd.name, help=cmd.help)(command)
