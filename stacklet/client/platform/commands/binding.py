# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from ..executor import StackletGraphqlExecutor, run_graphql, snippet_options
from ..graphql import StackletGraphqlSnippet


@StackletGraphqlExecutor.registry.register("list-bindings")
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


@StackletGraphqlExecutor.registry.register("show-binding")
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


@StackletGraphqlExecutor.registry.register("add-binding")
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


@StackletGraphqlExecutor.registry.register("update-binding")
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


@StackletGraphqlExecutor.registry.register("remove-binding")
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


@StackletGraphqlExecutor.registry.register("deploy-binding")
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


@StackletGraphqlExecutor.registry.register("run-binding")
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


@binding.command()
@snippet_options("list-bindings")
@click.pass_obj
def list(obj, **kwargs):
    """
    List bindings in Stacklet
    """
    click.echo(run_graphql(obj, name="list-bindings", variables=kwargs))


@binding.command()
@snippet_options("show-binding")
@click.pass_obj
def show(obj, **kwargs):
    """
    Show binding in Stacklet
    """
    click.echo(run_graphql(obj, name="show-binding", variables=kwargs))


@binding.command()
@snippet_options("add-binding")
@click.pass_obj
def add(obj, **kwargs):
    """
    Add binding in Stacklet
    """
    click.echo(run_graphql(obj, name="add-binding", variables=kwargs))


@binding.command()
@snippet_options("update-binding")
@click.pass_obj
def update(obj, **kwargs):
    """
    Update binding in Stacklet
    """
    click.echo(run_graphql(obj, name="update-binding", variables=kwargs))


@binding.command()
@snippet_options("remove-binding")
@click.pass_obj
def remove(obj, **kwargs):
    """
    Remove binding in Stacklet
    """
    click.echo(run_graphql(obj, name="remove-binding", variables=kwargs))


@binding.command()
@snippet_options("deploy-binding")
@click.pass_obj
def deploy(obj, **kwargs):
    """
    Deploy binding in Stacklet
    """
    click.echo(run_graphql(obj, name="deploy-binding", variables=kwargs))


@binding.command()
@snippet_options("run-binding")
@click.pass_obj
def run(obj, **kwargs):
    """
    Run a binding in Stacklet
    """
    click.echo(run_graphql(obj, name="run-binding", variables=kwargs))
