# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

import click

from ..context import StackletContext
from ..exceptions import InvalidInputException
from ..graphql.cli import GraphQLCommand, register_graphql_commands
from ..graphql.snippets import (
    AddPolicyCollection,
    AddPolicyCollectionItem,
    ListPolicyCollections,
    RemovePolicyCollection,
    RemovePolicyCollectionItem,
    ShowPolicyCollection,
    UpdatePolicyCollection,
)
from ..graphql.snippets.policy_collection import VIEW_OPTIONS


@click.group(short_help="Run policy collection queries/mutations")
def policy_collection(*args, **kwargs):
    """
    Manage policy collections
    """


# The view only exists on a dynamic collection, which is what --repository-uuid asks for.
_VIEW_ARGS = (*VIEW_OPTIONS, "start_rev_spec")


def _add_pre_check(context: StackletContext, cli_args: dict[str, Any]) -> dict[str, Any]:
    if not cli_args.get("repository_uuid"):
        if given := sorted(name for name in _VIEW_ARGS if cli_args.get(name)):
            options = ", ".join("--" + name.replace("_", "-") for name in given)
            raise InvalidInputException(
                f"{options} only applies to a dynamic policy collection, so it needs "
                "--repository-uuid too"
            )
    return cli_args


register_graphql_commands(
    policy_collection,
    [
        GraphQLCommand("list", ListPolicyCollections, "List policy collections in Stacklet"),
        GraphQLCommand(
            "add",
            AddPolicyCollection,
            "Add policy collection in Stacklet",
            pre_check=_add_pre_check,
        ),
        GraphQLCommand("show", ShowPolicyCollection, "Show policy collection in Stacklet"),
        GraphQLCommand("update", UpdatePolicyCollection, "Update policy collection in Stacklet"),
        GraphQLCommand(
            "add-item", AddPolicyCollectionItem, "Add item to policy collection in Stacklet"
        ),
        GraphQLCommand("remove", RemovePolicyCollection, "Remove policy collection in Stacklet"),
        GraphQLCommand(
            "remove-item",
            RemovePolicyCollectionItem,
            "Remove item from a policy collection in Stacklet",
        ),
    ],
)
