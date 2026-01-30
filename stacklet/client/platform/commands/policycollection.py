# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from ..graphql import GRAPHQL_SNIPPETS, StackletGraphqlSnippet
from ..graphql_cli import GraphQLCommand, register_graphql_commands


@GRAPHQL_SNIPPETS.register("list-policy-collections")
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


@GRAPHQL_SNIPPETS.register("show-policy-collection")
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


@GRAPHQL_SNIPPETS.register("add-policy-collection")
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


@GRAPHQL_SNIPPETS.register("update-policy-collection")
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


@GRAPHQL_SNIPPETS.register("add-policy-collection-item")
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


@GRAPHQL_SNIPPETS.register("remove-policy-collection-item")
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


@GRAPHQL_SNIPPETS.register("remove-policy-collection")
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


register_graphql_commands(
    policy_collection,
    [
        GraphQLCommand("list", "list-policy-collections", "List policy collections in Stacklet"),
        GraphQLCommand("add", "add-policy-collection", "Add policy collection in Stacklet"),
        GraphQLCommand("show", "show-policy-collection", "Show policy collection in Stacklet"),
        GraphQLCommand(
            "update", "update-policy-collection", "Update policy collection in Stacklet"
        ),
        GraphQLCommand(
            "add-item", "add-policy-collection-item", "Add item to policy collection in Stacklet"
        ),
        GraphQLCommand(
            "remove", "remove-policy-collection", "Remove policy collection in Stacklet"
        ),
        GraphQLCommand(
            "remove-item",
            "remove-policy-collection-item",
            "Remove item from a policy collection in Stacklet",
        ),
    ],
)
