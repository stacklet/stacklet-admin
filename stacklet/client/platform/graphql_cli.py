# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from typing import Any, Callable

import click

from .context import StackletContext
from .graphql import GRAPHQL_SNIPPETS
from .utils import PAGINATION_OPTIONS, wrap_command


def snippet_options(snippet_name):
    snippet = GRAPHQL_SNIPPETS.get(snippet_name)

    def wrapper(func):
        if not snippet:
            return func
        func = wrap_command(func, snippet.required, required=True)
        func = wrap_command(func, snippet.optional)
        if snippet.pagination:
            func = wrap_command(func, PAGINATION_OPTIONS)
        return func

    return wrapper


def run_graphql(context: StackletContext, name=None, variables=None, snippet=None, raw=False):
    if snippet:
        res = context.executor.run_query(snippet)
    else:
        res = context.executor.run(name, variables=variables)
    if raw:
        return res
    fmt = context.formatter()
    return fmt(res)


@dataclass
class GraphQLCommand:
    """A GraphlQL-based CLI command."""

    name: str
    snippet_name: str
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

    @snippet_options(cmd.snippet_name)
    @click.pass_obj
    def command(context: StackletContext, **cli_args):
        if cmd.pre_check:
            cli_args = cmd.pre_check(context, cli_args)

        click.echo(run_graphql(context, name=cmd.snippet_name, variables=cli_args))

    return click.command(name=cmd.name, help=cmd.help)(command)
