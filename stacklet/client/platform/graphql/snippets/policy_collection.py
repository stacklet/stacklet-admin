# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from ...utils import BOOL_CHOICE, to_bool
from ..snippet import GraphQLSnippet

# Shared selection for a policy collection node. `repositoryConfig`/`repositoryView`
# are only populated for dynamic collections; `repositoryView` is what says where in
# the repository the collection's policies are taken from.
FIELDS = """
            id
            uuid
            name
            description
            provider
            autoUpdate
            isDynamic
            repositoryConfig {
                uuid
                name
                url
            }
            repositoryView {
                uuid
                namespace
                branchName
                policyFileSuffix
                policyDirectories
                head
                lastScanned
            }
"""

# The policies in a collection. Listing only wants the count, so it selects no edges.
MAPPINGS = """
            policyMappings(first: 1000) {
                edges {
                    node {
                        id
                        policy {
                            uuid
                            name
                            version
                        }
                    }
                }
                pageInfo {
                    total
                }
            }
"""
MAPPING_COUNT = """
            policyMappings(first: 0) {
                pageInfo {
                    total
                }
            }
"""

# The view half of a dynamic collection's input. Every field sits on its own line so
# that unset options drop out individually; when they all drop the block collapses to
# `repositoryView: {}`, which the platform reads as "no view".
VIEW_INPUT = """
            branchName: $branch_name
            policyFileSuffix: $policy_file_suffix
            policyDirectories: $policy_directory
"""

# Options common to creating and updating a dynamic collection's view.
VIEW_OPTIONS = {
    "branch_name": "Dynamic collections: branch to take policies from",
    "policy_file_suffix": {
        "help": "Dynamic collections: only import policies from files with this suffix",
        "multiple": True,
    },
    "policy_directory": {
        "help": "Dynamic collections: only scan this directory for policies",
        "multiple": True,
    },
}
VIEW_TYPES = {
    "policy_file_suffix": "[String!]",
    "policy_directory": "[String!]",
}

AUTO_UPDATE_OPTION = {
    "auto_update": {
        "help": "Bump policies to their latest version as they are scanned",
        "type": BOOL_CHOICE,
    },
}


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
%(fields)s
%(mappings)s
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
    """ % {"fields": FIELDS, "mappings": MAPPING_COUNT}
    pagination_expr = "data.policyCollections.pageInfo"
    result_expr = "data.policyCollections.edges[].node"


class ShowPolicyCollection(GraphQLSnippet):
    name = "show-policy-collection"
    snippet = """
        query {
          policyCollection(
            uuid: $uuid
          ) {
%(fields)s
%(mappings)s
          }
      }
    """ % {"fields": FIELDS, "mappings": MAPPINGS}
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
        autoUpdate: $auto_update
        repositoryUUID: $repository_uuid
        repositoryView: {
%(view)s
            startRevSpec: $start_rev_spec
        }
      }){
        collection {
%(fields)s
%(mappings)s
        }
      }
    }
    """ % {"view": VIEW_INPUT, "fields": FIELDS, "mappings": MAPPINGS}
    required = {
        "name": "Policy Collection Name in Stacklet",
        "provider": "Cloud Provider",
    }

    optional = {
        "description": "Policy Collection Description",
        **AUTO_UPDATE_OPTION,
        "repository_uuid": (
            "Repository config UUID. Setting it makes this a dynamic collection, whose "
            "policies always match the latest scan of that repository"
        ),
        **VIEW_OPTIONS,
        "start_rev_spec": (
            "Dynamic collections: revision the first scan starts from. TAIL scans the "
            "whole history, recording a policy version per change -- a deep import. "
            "Only settable when the collection is created"
        ),
    }
    parameter_types = {"provider": "CloudProvider!", **VIEW_TYPES}
    variable_transformers = {"auto_update": to_bool}
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
        autoUpdate: $auto_update
        repositoryView: {
%(view)s
        }
      }){
        collection {
%(fields)s
%(mappings)s
        }
      }
    }
    """ % {"view": VIEW_INPUT, "fields": FIELDS, "mappings": MAPPINGS}
    required = {"uuid": "Policy Collection UUID"}

    optional = {
        "name": "Policy Collection Name in Stacklet",
        "provider": "Cloud Provider",
        "description": "Policy Collection Description",
        **AUTO_UPDATE_OPTION,
        **VIEW_OPTIONS,
    }
    parameter_types = dict(VIEW_TYPES)
    variable_transformers = {"auto_update": to_bool}


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
%(fields)s
%(mappings)s
            }
          }
      }
    """ % {"fields": FIELDS, "mappings": MAPPINGS}
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
%(fields)s
%(mappings)s
            }
          }
      }
    """ % {"fields": FIELDS, "mappings": MAPPINGS}
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
%(fields)s
%(mappings)s
        }
      }
    }
    """ % {"fields": FIELDS, "mappings": MAPPINGS}
    required = {"uuid": "Policy Collection UUID"}
