# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from ..graphql import GRAPHQL_SNIPPETS, StackletGraphqlSnippet
from ..graphql_cli import GraphQLCommand, register_graphql_commands


@GRAPHQL_SNIPPETS.register("list-bindings")
class QueryBindingsSnippet(StackletGraphqlSnippet):
    name = "list-bindings"
    snippet = """
        query {
          bindings(
            first: $first
            last: $last
            before: "$before"
            after: "$after"
          ) {
            edges {
              node {
                uuid
                name
                description
                schedule
                variables
                lastDeployed
                system
                accountGroup {
                    uuid
                    name
                }
                policyCollection {
                    uuid
                    name
                }
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


@GRAPHQL_SNIPPETS.register("show-binding")
class ShowBindingSnippet(StackletGraphqlSnippet):
    name = "show-binding"
    snippet = """
        query {
          binding(
            uuid: "$uuid"
          ) {
            uuid
            name
            description
            schedule
            variables
            lastDeployed
            system
            accountGroup {
                uuid
                name
            }
            policyCollection {
                uuid
                name
            }
          }
        }
    """

    required = {"uuid": "Binding UUID"}


@GRAPHQL_SNIPPETS.register("add-binding")
class AddBindingSnippet(StackletGraphqlSnippet):
    name = "add-binding"
    snippet = """
    mutation {
        addBinding(input:{
            name: "$name"
            accountGroupUUID: "$account_group_uuid"
            policyCollectionUUID: "$policy_collection_uuid"
            description: "$description"
            schedule: "$schedule"
            variables: "$variables"
            deploy: $deploy
        }){
            binding {
                uuid
                name
                description
                schedule
                variables
                lastDeployed
                accountGroup {
                    uuid
                    name
                }
                policyCollection {
                    uuid
                    name
                }
            }
        }
    }
    """

    required = {
        "name": "Binding Name",
        "account_group_uuid": "Account Group UUID",
        "policy_collection_uuid": "Policy Collection UUID",
    }

    optional = {
        "description": "Binding Description",
        "schedule": "Binding Schedule for Pull Mode Policies",
        "variables": "Binding variables (JSON Encoded string)",
        "deploy": {"help": "Deploy on creation true| false", "type": bool},
    }


@GRAPHQL_SNIPPETS.register("update-binding")
class UpdateBindingSnippet(StackletGraphqlSnippet):
    name = "update-binding"
    snippet = """
    mutation {
        updateBinding(input:{
            uuid: "$uuid"
            name: "$name"
            description: "$description"
            schedule: "$schedule"
            variables: "$variables"
        }){
            binding {
                uuid
                name
                description
                schedule
                variables
                lastDeployed
                accountGroup {
                    uuid
                    name
                }
                policyCollection {
                    uuid
                    name
                }
            }
        }
    }
    """

    required = {"uuid": "Binding UUID"}

    optional = {
        "name": "Binding Name",
        "description": "Binding Description",
        "schedule": "Binding Schedule for Pull Mode Policies",
        "variables": "Binding variables (JSON Encoded string)",
    }


@GRAPHQL_SNIPPETS.register("remove-binding")
class RemoveBindingSnippet(StackletGraphqlSnippet):
    name = "remove-binding"
    snippet = """
    mutation {
        removeBinding(uuid: "$uuid"){
            binding {
                id
                uuid
                name
                description
                schedule
                variables
                lastDeployed
                accountGroup {
                    uuid
                    name
                }
                policyCollection {
                    uuid
                    name
                }
            }
        }
    }
    """
    required = {"uuid": "Binding UUID"}


@GRAPHQL_SNIPPETS.register("deploy-binding")
class DeployBindingSnippet(StackletGraphqlSnippet):
    name = "deploy-binding"
    snippet = """
    mutation {
        deployBinding(uuid: "$uuid"){
            binding {
                uuid
                name
                description
                schedule
                variables
                lastDeployed
                accountGroup {
                    uuid
                    name
                }
                policyCollection {
                    uuid
                    name
                }
            }
        }
    }
    """

    required = {"uuid": "Binding UUID"}


@GRAPHQL_SNIPPETS.register("run-binding")
class RunBindingSnippet(StackletGraphqlSnippet):
    name = "run-binding"
    snippet = """
    mutation {
        runBinding(input:{uuid: "$uuid"}){
            binding {
                uuid
                name
                description
                schedule
                variables
                lastDeployed
                accountGroup {
                    uuid
                    name
                }
                policyCollection {
                    uuid
                    name
                }
            }
        }
    }
    """

    required = {"uuid": "Binding UUID"}


@click.group(short_help="Run binding queries/mutations")
def binding(*args, **kwargs):
    """
    Query and run mutations against bindings in Stacklet Platform
    """


register_graphql_commands(
    binding,
    [
        GraphQLCommand("list", "list-bindings", "List bindings in Stacklet"),
        GraphQLCommand("show", "show-binding", "Show binding in Stacklet"),
        GraphQLCommand("add", "add-binding", "Add binding in Stacklet"),
        GraphQLCommand("update", "update-binding", "Update binding in Stacklet"),
        GraphQLCommand("remove", "remove-binding", "Remove binding in Stacklet"),
        GraphQLCommand("deploy", "deploy-binding", "Deploy binding in Stacklet"),
        GraphQLCommand("run", "run-binding", "Run a binding in Stacklet"),
    ],
)
