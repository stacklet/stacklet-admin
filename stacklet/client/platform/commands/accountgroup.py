# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from stacklet.client.platform.executor import StackletGraphqlExecutor, _run_graphql, snippet_options
from stacklet.client.platform.graphql import StackletGraphqlSnippet
from stacklet.client.platform.utils import default_options


@StackletGraphqlExecutor.registry.register("list-account-groups")
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


@StackletGraphqlExecutor.registry.register("add-account-group")
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


@StackletGraphqlExecutor.registry.register("update-account-group")
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


@StackletGraphqlExecutor.registry.register("show-account-group")
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


@StackletGraphqlExecutor.registry.register("remove-account-group")
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


@StackletGraphqlExecutor.registry.register("add-account-group-item")
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


@StackletGraphqlExecutor.registry.register("remove-account-group-item")
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
@default_options()
def account_group(*args, **kwargs):
    """
    Manage account groups
    """


@account_group.command()
@snippet_options("list-account-groups")
@click.pass_obj
def list(obj, **kwargs):
    """
    List account groups in Stacklet
    """
    click.echo(_run_graphql(obj, name="list-account-groups", variables=kwargs))


@account_group.command()
@snippet_options("add-account-group")
@click.pass_obj
def add(obj, **kwargs):
    """
    Add account group
    """
    click.echo(_run_graphql(obj, name="add-account-group", variables=kwargs))


@account_group.command()
@snippet_options("update-account-group")
@click.pass_obj
def update(obj, **kwargs):
    """
    Update account group
    """
    click.echo(_run_graphql(obj, name="update-account-group", variables=kwargs))


@account_group.command()
@snippet_options("show-account-group")
@click.pass_obj
def show(obj, **kwargs):
    """
    Show account group
    """
    click.echo(_run_graphql(obj, name="show-account-group", variables=kwargs))


@account_group.command()
@snippet_options("remove-account-group")
@click.pass_obj
def remove(obj, **kwargs):
    """
    Remove account group
    """
    click.echo(_run_graphql(obj, name="remove-account-group", variables=kwargs))


@account_group.command()
@snippet_options("add-account-group-item")
@click.pass_obj
def add_item(obj, **kwargs):
    """
    Add account group item
    """
    click.echo(_run_graphql(obj, name="add-account-group-item", variables=kwargs))


@account_group.command()
@snippet_options("remove-account-group-item")
@click.pass_obj
def remove_item(obj, **kwargs):
    """
    Remove account group item
    """
    click.echo(_run_graphql(obj, name="remove-account-group-item", variables=kwargs))
