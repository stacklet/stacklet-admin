# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from stacklet.client.platform.executor import _run_graphql
from stacklet.client.platform.executor import StackletGraphqlExecutor, snippet_options
from stacklet.client.platform.graphql import StackletGraphqlSnippet
from stacklet.client.platform.utils import click_group_entry, default_options


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
@default_options()
@click.pass_context
def binding(*args, **kwargs):
    """
    Query and run mutations against bindings in Stacklet Platform
    """
    click_group_entry(*args, **kwargs)


@binding.command()
@snippet_options("list-bindings")
@click.pass_context
def list(ctx, **kwargs):
    """
    List bindings in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="list-bindings", variables=kwargs))


@binding.command()
@snippet_options("show-binding")
@click.pass_context
def show(ctx, **kwargs):
    """
    Show binding in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="show-binding", variables=kwargs))


@binding.command()
@snippet_options("add-binding")
@click.pass_context
def add(ctx, **kwargs):
    """
    Add binding in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="add-binding", variables=kwargs))


@binding.command()
@snippet_options("update-binding")
@click.pass_context
def update(ctx, **kwargs):
    """
    Update binding in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="update-binding", variables=kwargs))


@binding.command()
@snippet_options("remove-binding")
@click.pass_context
def remove(ctx, **kwargs):
    """
    Remove binding in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="remove-binding", variables=kwargs))


@binding.command()
@snippet_options("deploy-binding")
@click.pass_context
def deploy(ctx, **kwargs):
    """
    Deploy binding in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="deploy-binding", variables=kwargs))


@binding.command()
@snippet_options("run-binding")
@click.pass_context
def run(ctx, **kwargs):
    """
    Run a binding in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="run-binding", variables=kwargs))
