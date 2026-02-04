# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

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


@click.group(short_help="Run policy collection queries/mutations")
def policy_collection(*args, **kwargs):
    """
    Manage policy collections
    """


register_graphql_commands(
    policy_collection,
    [
        GraphQLCommand("list", ListPolicyCollections, "List policy collections in Stacklet"),
        GraphQLCommand("add", AddPolicyCollection, "Add policy collection in Stacklet"),
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
