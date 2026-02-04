# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from ..snippet import GraphQLSnippet


class ListPolicyCollections(GraphQLSnippet):
    name = "list-policy-collections"
    snippet = """
        query {
          policyCollections(
            first: $first
            last: $last
            before: $before
            after: $after
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
    pagination_expr = "data.policyCollections.pageInfo"
    result_expr = "data.policyCollections.edges[].node"


class ShowPolicyCollection(GraphQLSnippet):
    name = "show-policy-collection"
    snippet = """
        query {
          policyCollection(
            uuid: $uuid
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
    result_expr = "data.policyCollection"


class AddPolicyCollection(GraphQLSnippet):
    name = "add-policy-collection"
    snippet = """
    mutation {
      addPolicyCollection(input:{
        name: $name
        provider: $provider
        description: $description
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
    result_expr = "data.addPolicyCollection.collection"


class UpdatePolicyCollection(GraphQLSnippet):
    name = "update-policy-collection"
    snippet = """
    mutation {
      updatePolicyCollection(input:{
        uuid: $uuid
        name: $name
        provider: $provider
        description: $description
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


class AddPolicyCollectionItem(GraphQLSnippet):
    name = "add-policy-collection-item"
    snippet = """
        mutation {
          addPolicyCollectionItems(input:{
            uuid: $uuid
            items: [
                {
                    policyUUID: $policy_uuid
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


class RemovePolicyCollectionItem(GraphQLSnippet):
    name = "remove-policy-collection-item"
    snippet = """
        mutation {
          removePolicyCollectionItems(input:{
            uuid: $uuid
            items: [
                {
                    policyUUID: $policy_uuid
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


class RemovePolicyCollection(GraphQLSnippet):
    name = "remove-policy-collection"
    snippet = """
    mutation {
      removePolicyCollection(
        uuid: $uuid
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
