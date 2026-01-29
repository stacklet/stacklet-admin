# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from ..graphql import GRAPHQL_SNIPPETS, StackletGraphqlSnippet
from ..graphql_cli import GraphQLCommand, register_graphql_commands


@GRAPHQL_SNIPPETS.register("list-account-groups")
class QueryAccountGroupSnippet(StackletGraphqlSnippet):
    name = "list-account-groups"
    snippet = """
        query {
          accountGroups(
            first: $first
            last: $last
            before: "$before"
            after: "$after"
          ) {
            edges {
              node {
                id
                uuid
                name
                shortName
                provider
                description
                regions
                variables
                priority
                itemCount
              }
            }
            pageInfo {
              hasPreviousPage
              hasNextPage
              startCursor
              endCursor
              total
            }
          }
        }
    """
    pagination = True


@GRAPHQL_SNIPPETS.register("add-account-group")
class AddAccountGroupSnippet(StackletGraphqlSnippet):
    name = "add-account-group"
    snippet = """
    mutation {
      addAccountGroup(input:{
        name: "$name"
        provider: $provider
        regions: $region
        shortName: "$short_name"
        description: "$description"
        variables: "$variables"
        priority: $priority
      }){
        group {
            name
            uuid
            id
            shortName
            provider
            description
            regions
            variables
            priority
            itemCount
            items {
                uuid
                key
                provider
                name
                regions
            }
        }
      }
    }
    """
    required = {
        "name": "Account Name in Stacklet",
        "provider": "Cloud Provider",
    }

    parameter_types = {
        "provider": "CloudProvider!",
    }

    optional = {
        "description": "Account Group Description",
        "short_name": "Account Group Short Name",
        "variables": "Account Group Variables (JSON encoded)",
        "priority": "Account Group priority (0-99)",
        "region": {"help": "Cloud Regions", "multiple": True},
    }


@GRAPHQL_SNIPPETS.register("update-account-group")
class UpdateAccountSnippet(StackletGraphqlSnippet):
    name = "update-account-group"
    snippet = """
    mutation {
      updateAccountGroup(input:{
        uuid: "$uuid"
        name: "$name"
        shortName: "$short_name"
        description: "$description"
        regions: $region
        variables: "$variables"
        priority: $priority
      }){
        group {
            name
            uuid
            id
            shortName
            provider
            description
            regions
            variables
            priority
            itemCount
            items {
                uuid
                key
                provider
                name
                regions
            }
        }
      }
    }
    """
    required = {
        "uuid": "Account Group UUID",
    }

    optional = {
        "region": {"help": "Cloud Regions", "multiple": True},
        "name": "Account Group Name",
        "description": "Account Group Description",
        "short_name": "Account Group Short Name",
        "variables": "Account Group Variables (JSON encoded)",
        "priority": "Account Group priority (0-99)",
    }


@GRAPHQL_SNIPPETS.register("show-account-group")
class ShowAccountGroup(StackletGraphqlSnippet):
    name = "show-account-group"
    snippet = """
        query {
          accountGroup(
            uuid: "$uuid"
          ) {
            name
            uuid
            id
            shortName
            provider
            description
            regions
            variables
            priority
            itemCount
            items {
                uuid
                key
                provider
                name
                regions
            }
          }
      }
    """
    required = {"uuid": "Account group UUID"}


@GRAPHQL_SNIPPETS.register("remove-account-group")
class RemoveAccountGroup(StackletGraphqlSnippet):
    name = "remove-account-group"
    snippet = """
        mutation {
          removeAccountGroup(
            uuid: "$uuid"
          ) {
              group {
                name
                uuid
                id
                shortName
                provider
                description
                regions
                variables
                priority
                itemCount
                items {
                    uuid
                    key
                    provider
                    name
                    regions
                }
            }
          }
      }
    """
    required = {"uuid": "Account group UUID"}


@GRAPHQL_SNIPPETS.register("add-account-group-item")
class AddAccountGroupItem(StackletGraphqlSnippet):
    name = "add-account-group-item"
    snippet = """
        mutation {
          addAccountGroupItems(input:{
            uuid: "$uuid"
            items: [
                {
                    key: "$key"
                    provider: $provider
                }
            ]
          }) {
              group {
                name
                uuid
                id
                shortName
                provider
                description
                regions
                variables
                priority
                itemCount
                items {
                    uuid
                    key
                    provider
                    name
                    regions
                }
            }
          }
      }
    """
    required = {
        "uuid": "Account group UUID",
        "key": "Account Key",
        "provider": "Account Provider",
    }
    parameter_types = {"provider": "CloudProvider!"}
    optional = {"regions": "Account Regions"}


@GRAPHQL_SNIPPETS.register("remove-account-group-item")
class RemoveAccountGroupItem(StackletGraphqlSnippet):
    name = "remove-account-group-item"
    snippet = """
        mutation {
          removeAccountGroupItems(input:{
            uuid: "$uuid"
            items: [
                {
                    key: "$key"
                    provider: $provider
                }
            ]
          }) {
              group {
                name
                uuid
                id
                shortName
                provider
                description
                regions
                variables
                priority
                itemCount
                items {
                    uuid
                    key
                    provider
                    name
                    regions
                }
            }
          }
      }
    """
    required = {
        "uuid": "Account group UUID",
        "key": "Account Key",
        "provider": "Account Provider",
    }

    parameter_types = {"provider": "CloudProvider!"}


@click.group("account-group", short_help="Run account group queries/mutations")
def account_group(*args, **kwargs):
    """
    Manage account groups
    """


register_graphql_commands(
    account_group,
    [
        GraphQLCommand("list", "list-account-groups", "List account groups in Stacklet"),
        GraphQLCommand("add", "add-account-group", "Add account group"),
        GraphQLCommand("update", "update-account-group", "Update account group"),
        GraphQLCommand("show", "show-account-group", "Show account group"),
        GraphQLCommand("remove", "remove-account-group", "Remove account group"),
        GraphQLCommand("add-item", "add-account-group-item", "Add account group item"),
        GraphQLCommand("remove-item", "remove-account-group-item", "Remove account group item"),
    ],
)
