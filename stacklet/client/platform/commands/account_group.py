# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

import click
import jmespath

from ..context import StackletContext
from ..exceptions import InvalidInputException
from ..graphql.cli import GraphQLCommand, register_graphql_commands
from ..graphql.snippet import GraphQLSnippet
from ..graphql.snippets import (
    AddAccountGroup,
    AddAccountGroupItem,
    ListAccountGroups,
    RemoveAccountGroup,
    RemoveAccountGroupItem,
    ShowAccountGroup,
    UpdateAccountGroup,
)


@click.group("account-group", short_help="Run account group queries/mutations")
def account_group(*args, **kwargs):
    """
    Manage account groups
    """


class _FindAccountGroupMapping(GraphQLSnippet):
    """Internal lookup used to resolve a mapping id from an account key/provider."""

    name = "_find-account-group-mapping"
    snippet = """
        query {
          accountGroup(uuid: $uuid) {
            accountMappings(first: 1000) {
                edges {
                    node {
                        id
                        account {
                            key
                            provider
                        }
                    }
                }
            }
          }
      }
    """
    required = {"uuid": "Account group UUID"}


def _remove_item_pre_check(context: StackletContext, cli_args: dict[str, Any]) -> dict[str, Any]:
    """
    removeAccountGroupMappings needs the mapping's node id, but the CLI still accepts
    the account's key/provider, so look up the id before running the mutation.
    """
    group_uuid = cli_args["uuid"]
    key = cli_args["key"]
    provider = cli_args["provider"]

    res = context.executor.run_snippet(_FindAccountGroupMapping, variables={"uuid": group_uuid})
    edges = jmespath.search("data.accountGroup.accountMappings.edges", res) or []
    for edge in edges:
        account = edge["node"]["account"]
        if account["key"] == key and account["provider"].upper() == provider.upper():
            return {"mapping_id": edge["node"]["id"]}

    raise InvalidInputException(
        f"No account with key={key!r} provider={provider!r} found in account group {group_uuid!r}"
    )


register_graphql_commands(
    account_group,
    [
        GraphQLCommand("list", ListAccountGroups, "List account groups in Stacklet"),
        GraphQLCommand("add", AddAccountGroup, "Add account group"),
        GraphQLCommand("update", UpdateAccountGroup, "Update account group"),
        GraphQLCommand("show", ShowAccountGroup, "Show account group"),
        GraphQLCommand("remove", RemoveAccountGroup, "Remove account group"),
        GraphQLCommand("add-item", AddAccountGroupItem, "Add account group item"),
        GraphQLCommand(
            "remove-item",
            RemoveAccountGroupItem,
            "Remove account group item",
            pre_check=_remove_item_pre_check,
        ),
    ],
)
