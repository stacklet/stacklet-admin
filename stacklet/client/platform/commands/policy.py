# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

import click

from ..context import StackletContext
from ..exceptions import InvalidInputException
from ..graphql.snippets import ListPolicies, ShowPolicy
from ..graphql_cli import GraphQLCommand, register_graphql_commands, run_graphql, snippet_options


@click.group(short_help="Run policy queries")
def policy(*args, **kwargs):
    """
    Manage policies
    """


def _show_policy_pre_check(context: StackletContext, cli_args: dict[str, Any]) -> dict[str, Any]:
    """Validate that either name or uuid is provided, but not both."""
    if all([cli_args.get("name"), cli_args.get("uuid")]):
        raise InvalidInputException("Either name or uuid can be set, but not both")
    if not any([cli_args.get("name"), cli_args.get("uuid")]):
        raise InvalidInputException("Either name or uuid must be set")
    return cli_args


register_graphql_commands(
    policy,
    [
        GraphQLCommand("list", ListPolicies, "List policies in Stacklet"),
        GraphQLCommand(
            "show",
            ShowPolicy,
            "Show policy in Stacklet by either name or uuid",
            pre_check=_show_policy_pre_check,
        ),
    ],
)


@policy.command()
@snippet_options(ShowPolicy)
@click.pass_obj
def show_source(obj, **kwargs):
    """
    Show policy source in Stacklet by either name or uuid
    """
    _show_policy_pre_check(obj, kwargs)
    click.echo(
        run_graphql(obj, snippet_class=ShowPolicy, variables=kwargs, raw=True)["data"]["policy"][
            "sourceYAML"
        ]
    )
