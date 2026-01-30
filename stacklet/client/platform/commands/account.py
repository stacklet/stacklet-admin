# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json

import click

from ..graphql import GRAPHQL_SNIPPETS, StackletGraphqlSnippet
from ..graphql_cli import GraphQLCommand, register_graphql_commands, run_graphql, snippet_options


@GRAPHQL_SNIPPETS.register("list-accounts")
class ListAccountsSnippet(StackletGraphqlSnippet):
    name = "list-accounts"
    snippet = """
        query {
          accounts(
            first: $first
            last: $last
            before: "$before"
            after: "$after"
          ) {
            edges {
              node {
                id
                key
                name
                shortName
                description
                provider
                path
                email
                securityContext
                tags {
                    key
                    value
                }
                variables
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


@GRAPHQL_SNIPPETS.register("show-account")
class QueryAccountSnippet(StackletGraphqlSnippet):
    name = "show-account"
    snippet = """
        query {
          account(
            provider: $provider
            key: "$key"
          ) {
            id
            key
            active
            name
            shortName
            description
            provider
            path
            email
            securityContext
            tags {
                key
                value
            }
            variables
          }
        }
    """

    required = {
        "provider": "Account Provider: AWS | Azure | GCP | Kubernetes",
        "key": "Account key -- Account ID for AWS, Subscription ID for Azure, Project ID for GCP",
    }

    parameter_types = {"provider": "CloudProvider!"}


@GRAPHQL_SNIPPETS.register("update-account")
class UpdateAccountSnippet(StackletGraphqlSnippet):
    name = "update-account"
    snippet = """
    mutation {
      updateAccount(input:{
        provider:$provider
        key: "$key"
        name: "$name"
        email: "$email"
        description: "$description"
        shortName: "$short_name"
        tags: $tags
        variables: "$variables"
        securityContext: "$security_context"
      }){
        account {
            id
            key
            name
            shortName
            description
            provider
            path
            email
            securityContext
            tags {
                key
                value
            }
            variables
        }
      }
    }
    """

    required = {
        "provider": "Account Provider: AWS | Azure | GCP | Kubernetes",
        "key": "Account key -- Account ID for AWS, Subscription ID for Azure, Project ID for GCP",
    }
    optional = {
        "name": "Account Name",
        "email": "Account Email Address",
        "security_context": "Role for Custodian policy execution",
        "short_name": "Short Name for Account",
        "description": "Description for Account",
        "tags": 'List of tags for Account, e.g. --tags "[{key: \\"department\\", value: \\"marketing\\"}]"',  # noqa
        "variables": 'JSON encoded string of variables e.g. --variables \'{\\\\"foo\\\\": \\\\"bar\\\\"}\'',  # noqa
    }
    parameter_types = {"provider": "CloudProvider!", "tags": "[TagInput!]"}
    variable_transformers = {"tags": lambda x: json.loads(x) if x is not None else []}


@GRAPHQL_SNIPPETS.register("add-account")
class AddAccountSnippet(StackletGraphqlSnippet):
    name = "add-account"
    snippet = """
    mutation {
      addAccount(input:{
        provider: $provider
        key:"$key"
        name:"$name"
        path:"$path"
        email:"$email"
        securityContext:"$security_context"
        shortName: "$short_name"
        description: "$description"
        tags: $tags
        variables: "$variables"
      }){
        account {
            id
            key
            name
            shortName
            description
            provider
            path
            email
            securityContext
            tags {
                key
                value
            }
            variables
        }
      }
    }
    """
    parameter_types = {"provider": "CloudProvider!", "tags": "[TagInput!]"}
    required = {
        "name": "Account Name in Stacklet",
        "key": "Account key -- Account ID for AWS, Subscription ID for Azure, Project ID for GCP",
        "provider": "Account Provider: AWS | Azure | GCP | Kubernetes",
        "security_context": "Role for Custodian policy execution",
    }
    optional = {
        "path": "Account Path",
        "email": "Account Email Address",
        "short_name": "Short Name for Account",
        "description": "Description for Account",
        "tags": 'List of tags for Account, e.g. --tags "[{key: \\"department\\", value: \\"marketing\\"}]"',  # noqa
        "variables": 'JSON encoded string of variables e.g. --variables \'{"foo": "bar"}\'',  # noqa
    }
    variable_transformers = {"tags": lambda x: json.loads(x) if x is not None else []}


@GRAPHQL_SNIPPETS.register("remove-account")
class RemoveAccountSnippet(StackletGraphqlSnippet):
    name = "remove-account"
    snippet = """
    mutation {
      removeAccount(
        provider: $provider,
        key:"$key",
      ){
        account {
            id
            key
            name
            shortName
            description
            provider
            path
            email
            securityContext
            tags {
                key
                value
            }
            variables
        }
      }
    }
    """
    required = {
        "provider": "Account Provider: AWS | Azure | GCP | Kubernetes",
        "key": "Account key -- Account ID for AWS, Subscription ID for Azure, Project ID for GCP",
    }

    parameter_types = {"provider": "CloudProvider!"}


@GRAPHQL_SNIPPETS.register("validate-account")
class ValidateAccountSnippet(StackletGraphqlSnippet):
    name = "validate-account"
    snippet = """
    mutation {
      validateAccount(
        input: {
          provider: $provider,
          key:"$key",
        }
      ){
        account {
            id
            key
            name
            shortName
            description
            provider
            path
            email
            securityContext
            tags {
                key
                value
            }
            variables
            status
            status_message
        }
      }
    }
    """
    required = {
        "provider": "Account Provider: AWS | Azure | GCP | Kubernetes",
        "key": "Account key -- Account ID for AWS, Subscription ID for Azure, Project ID for GCP",
    }

    parameter_types = {"provider": "CloudProvider!"}


@click.group(short_help="Run account queries/mutations")
def account(*args, **kwargs):
    """Query against and Run mutations against Account objects in Stacklet."""


register_graphql_commands(
    account,
    [
        GraphQLCommand("list", "list-accounts", "List cloud accounts in Stacklet"),
        GraphQLCommand("add", "add-account", "Add an account to Stacklet"),
        GraphQLCommand("remove", "remove-account", "Remove an account from Stacklet"),
        GraphQLCommand("update", "update-account", "Update an account in Stacklet"),
        GraphQLCommand("show", "show-account", "Show an account in Stacklet"),
        GraphQLCommand("validate", "validate-account", "Validate an account in Stacklet"),
    ],
)


@account.command()
@snippet_options("list-accounts")
@click.pass_obj
def validate_all(obj, **kwargs):
    """Validate all accounts in Stacklet"""
    executor = obj.executor
    result = executor.run("list-accounts", variables=kwargs)

    # get all the accounts
    count = result["data"]["accounts"]["pageInfo"]["total"]
    kwargs["last"] = count

    result = executor.run("list-accounts", variables=kwargs)
    account_provider_pairs = [
        {"provider": r["node"]["provider"], "key": r["node"]["key"]}
        for r in result["data"]["accounts"]["edges"]
    ]
    for pair in account_provider_pairs:
        click.echo(run_graphql(obj, name="validate-account", variables=pair))
