# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from ..graphql.snippets import (
    AddBinding,
    DeployBinding,
    ListBindings,
    RemoveBinding,
    RunBinding,
    ShowBinding,
    UpdateBinding,
)
from ..graphql_cli import GraphQLCommand, register_graphql_commands


@click.group(short_help="Run binding queries/mutations")
def binding(*args, **kwargs):
    """
    Query and run mutations against bindings in Stacklet Platform
    """


register_graphql_commands(
    binding,
    [
        GraphQLCommand("list", ListBindings, "List bindings in Stacklet"),
        GraphQLCommand("show", ShowBinding, "Show binding in Stacklet"),
        GraphQLCommand("add", AddBinding, "Add binding in Stacklet"),
        GraphQLCommand("update", UpdateBinding, "Update binding in Stacklet"),
        GraphQLCommand("remove", RemoveBinding, "Remove binding in Stacklet"),
        GraphQLCommand("deploy", DeployBinding, "Deploy binding in Stacklet"),
        GraphQLCommand("run", RunBinding, "Run a binding in Stacklet"),
    ],
)
