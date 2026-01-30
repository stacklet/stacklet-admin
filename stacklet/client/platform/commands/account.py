# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0


import click

from ..graphql.snippets import (
    AddAccount,
    ListAccounts,
    RemoveAccount,
    ShowAccount,
    UpdateAccount,
    ValidateAccount,
)
from ..graphql_cli import GraphQLCommand, register_graphql_commands, run_graphql, snippet_options


@click.group(short_help="Run account queries/mutations")
def account(*args, **kwargs):
    """Query against and Run mutations against Account objects in Stacklet."""


register_graphql_commands(
    account,
    [
        GraphQLCommand("list", ListAccounts, "List cloud accounts in Stacklet"),
        GraphQLCommand("add", AddAccount, "Add an account to Stacklet"),
        GraphQLCommand("remove", RemoveAccount, "Remove an account from Stacklet"),
        GraphQLCommand("update", UpdateAccount, "Update an account in Stacklet"),
        GraphQLCommand("show", ShowAccount, "Show an account in Stacklet"),
        GraphQLCommand("validate", ValidateAccount, "Validate an account in Stacklet"),
    ],
)


@account.command()
@snippet_options(ListAccounts)
@click.pass_obj
def validate_all(obj, **kwargs):
    """Validate all accounts in Stacklet"""
    executor = obj.executor
    result = executor.run_snippet(ListAccounts, variables=kwargs)

    # get all the accounts
    count = result["data"]["accounts"]["pageInfo"]["total"]
    kwargs["last"] = count

    result = executor.run_snippet(ListAccounts, variables=kwargs)
    account_provider_pairs = [
        {"provider": r["node"]["provider"], "key": r["node"]["key"]}
        for r in result["data"]["accounts"]["edges"]
    ]
    for pair in account_provider_pairs:
        click.echo(run_graphql(obj, snippet_class=ValidateAccount, variables=pair))
