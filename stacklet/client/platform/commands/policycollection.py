# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from ..executor import StackletGraphqlExecutor, _run_graphql, snippet_options
from ..graphql import StackletGraphqlSnippet


@StackletGraphqlExecutor.registry.register("list-policy-collections")
class QueryPolicyCollectionSnippet(StackletGraphqlSnippet):
    name = "list-policy-collections"
    snippet = """
        query {
          policyCollections(
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
                description
                provider
                repository
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


@StackletGraphqlExecutor.registry.register("show-policy-collection")
class ShowPolicyCollection(StackletGraphqlSnippet):
    name = "show-policy-collection"
    snippet = """
        query {
          policyCollection(
            uuid: "$uuid"
          ) {
            id
            uuid
            name
            description
            provider
            repository
            itemCount
            items {
                uuid
                name
                version
            }
          }
      }
    """
    required = {"uuid": "Policy Collection UUID"}


@StackletGraphqlExecutor.registry.register("add-policy-collection")
class AddPolicyCollection(StackletGraphqlSnippet):
    name = "add-policy-collection"
    snippet = """
    mutation {
      addPolicyCollection(input:{
        name: "$name"
        provider: $provider
        description: "$description"
      }){
        collection {
            id
            uuid
            name
            description
            provider
            repository
            itemCount
            items {
                uuid
                name
                version
            }
        }
      }
    }
    """
    required = {
        "name": "Policy Collection Name in Stacklet",
        "provider": "Cloud Provider",
    }

    optional = {
        "description": "Policy Collection Description",
    }

    parameter_types = {"provider": "CloudProvider!"}


@StackletGraphqlExecutor.registry.register("update-policy-collection")
class UpdatePolicyCollection(StackletGraphqlSnippet):
    name = "update-policy-collection"
    snippet = """
    mutation {
      updatePolicyCollection(input:{
        uuid: "$uuid"
        name: "$name"
        provider: $provider
        description: "$description"
      }){
        collection {
            id
            uuid
            name
            description
            provider
            repository
            itemCount
            items {
                uuid
                name
                version
            }
        }
      }
    }
    """
    required = {"uuid": "Policy Collection UUID"}

    optional = {
        "name": "Policy Collection Name in Stacklet",
        "provider": "Cloud Provider",
        "description": "Policy Collection Description",
    }


@StackletGraphqlExecutor.registry.register("add-policy-collection-item")
class AddPolicyCollectionItem(StackletGraphqlSnippet):
    name = "add-policy-collection-item"
    snippet = """
        mutation {
          addPolicyCollectionItems(input:{
            uuid: "$uuid"
            items: [
                {
                    policyUUID: "$policy_uuid"
                    policyVersion: $policy_version
                }
            ]
          }) {
              collection {
                id
                uuid
                name
                description
                provider
                repository
                itemCount
                items {
                    uuid
                    name
                    version
                }
            }
          }
      }
    """
    required = {
        "uuid": "Account group UUID",
        "policy_uuid": "Policy UUID",
    }

    optional = {"policy_version": "Policy Version"}
    variable_transformers = {"policy_version": lambda x: x and int(x)}


@StackletGraphqlExecutor.registry.register("remove-policy-collection-item")
class RemovePolicyCollectionItem(StackletGraphqlSnippet):
    name = "remove-policy-collection-item"
    snippet = """
        mutation {
          removePolicyCollectionItems(input:{
            uuid: "$uuid"
            items: [
                {
                    policyUUID: "$policy_uuid"
                    policyVersion: $policy_version
                }
            ]
          }) {
              collection {
                id
                uuid
                name
                description
                provider
                repository
                itemCount
                items {
                    uuid
                    name
                    version
                }
            }
          }
      }
    """
    required = {
        "uuid": "Account group UUID",
        "policy_uuid": "Policy UUID",
    }

    optional = {"policy_version": "Policy Version"}


@StackletGraphqlExecutor.registry.register("remove-policy-collection")
class RemovePolicyCollection(StackletGraphqlSnippet):
    name = "remove-policy-collection"
    snippet = """
    mutation {
      removePolicyCollection(
        uuid: "$uuid"
      ){
        collection {
            id
            uuid
            name
            description
            provider
            repository
            itemCount
            items {
                uuid
                name
                version
            }
        }
      }
    }
    """
    required = {"uuid": "Policy Collection UUID"}


@click.group(short_help="Run policy collection queries/mutations")
def policy_collection(*args, **kwargs):
    """
    Manage policy collections
    """


@policy_collection.command()
@snippet_options("list-policy-collections")
@click.pass_obj
def list(obj, **kwargs):
    """
    List policy collections in Stacklet
    """
    click.echo(_run_graphql(obj, name="list-policy-collections", variables=kwargs))


@policy_collection.command()
@snippet_options("add-policy-collection")
@click.pass_obj
def add(obj, **kwargs):
    """
    Add policy collection in Stacklet
    """
    click.echo(_run_graphql(obj, name="add-policy-collection", variables=kwargs))


@policy_collection.command()
@snippet_options("show-policy-collection")
@click.pass_obj
def show(obj, **kwargs):
    """
    Show policy collection in Stacklet
    """
    click.echo(_run_graphql(obj, name="show-policy-collection", variables=kwargs))


@policy_collection.command()
@snippet_options("update-policy-collection")
@click.pass_obj
def update(obj, **kwargs):
    """
    Update policy collection in Stacklet
    """
    click.echo(_run_graphql(obj, name="update-policy-collection", variables=kwargs))


@policy_collection.command()
@snippet_options("add-policy-collection-item")
@click.pass_obj
def add_item(obj, **kwargs):
    """
    Add item to policy collection in Stacklet
    """
    click.echo(_run_graphql(obj, name="add-policy-collection-item", variables=kwargs))


@policy_collection.command()
@snippet_options("remove-policy-collection")
@click.pass_obj
def remove(obj, **kwargs):
    """
    Remove policy collection in Stacklet
    """
    click.echo(_run_graphql(obj, name="remove-policy-collection", variables=kwargs))


@policy_collection.command()
@snippet_options("remove-policy-collection-item")
@click.pass_obj
def remove_item(obj, **kwargs):
    """
    Remove item from a policy collection in Stacklet
    """
    click.echo(_run_graphql(obj, name="remove-policy-collection-item", variables=kwargs))
