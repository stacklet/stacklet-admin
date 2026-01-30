# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from ..graphql.snippets import (
    AddAccountGroup,
    AddAccountGroupItem,
    ListAccountGroups,
    RemoveAccountGroup,
    RemoveAccountGroupItem,
    ShowAccountGroup,
    UpdateAccountGroup,
)
from ..graphql_cli import GraphQLCommand, register_graphql_commands


@click.group("account-group", short_help="Run account group queries/mutations")
def account_group(*args, **kwargs):
    """
    Manage account groups
    """


register_graphql_commands(
    account_group,
    [
        GraphQLCommand("list", ListAccountGroups, "List account groups in Stacklet"),
        GraphQLCommand("add", AddAccountGroup, "Add account group"),
        GraphQLCommand("update", UpdateAccountGroup, "Update account group"),
        GraphQLCommand("show", ShowAccountGroup, "Show account group"),
        GraphQLCommand("remove", RemoveAccountGroup, "Remove account group"),
        GraphQLCommand("add-item", AddAccountGroupItem, "Add account group item"),
        GraphQLCommand("remove-item", RemoveAccountGroupItem, "Remove account group item"),
    ],
)
