# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any

import click

from ..context import StackletContext
from ..exceptions import InvalidInputException
from ..graphql.snippets import (
    AddRepository,
    ListRepository,
    ProcessRepository,
    RemoveRepository,
    ScanRepository,
    ShowRepository,
)
from ..graphql_cli import GraphQLCommand, register_graphql_commands


@click.group(short_help="Run repository queries/mutations")
def repository(*args, **kwargs):
    """Query against and Run mutations against Repository objects in Stacklet"""


def _add_pre_check(context: StackletContext, cli_args: dict[str, Any]) -> dict[str, Any]:
    private_key = cli_args.get("ssh_private_key")
    auth_user = cli_args.get("auth_user")
    if private_key:
        if auth_user is None:
            raise InvalidInputException("Both --auth-user and --ssh-private-key are required")
        with open(os.path.expanduser(private_key), "r") as f:
            cli_args["ssh_private_key"] = f.read().strip("\n")

    return cli_args


register_graphql_commands(
    repository,
    [
        GraphQLCommand("process", ProcessRepository, "Process a Policy Repository in Stacklet"),
        GraphQLCommand("list", ListRepository, "List repositories"),
        GraphQLCommand(
            "add", AddRepository, "Add a Policy repository to Stacklet", pre_check=_add_pre_check
        ),
        GraphQLCommand("remove", RemoveRepository, "Remove a Policy Repository to Stacklet"),
        GraphQLCommand("scan", ScanRepository, "Scan a repository for policies"),
        GraphQLCommand("show", ShowRepository, "Show a repository"),
    ],
)
