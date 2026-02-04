# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from ..snippet import GraphQLSnippet


class ListBindings(GraphQLSnippet):
    name = "list-bindings"
    snippet = """
        query {
          bindings(
            first: $first
            last: $last
            before: $before
            after: $after
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


class ShowBinding(GraphQLSnippet):
    name = "show-binding"
    snippet = """
        query {
          binding(
            uuid: $uuid
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


class AddBinding(GraphQLSnippet):
    name = "add-binding"
    snippet = """
    mutation {
        addBinding(input:{
            name: $name
            accountGroupUUID: $account_group_uuid
            policyCollectionUUID: $policy_collection_uuid
            description: $description
            schedule: $schedule
            variables: $variables
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


class UpdateBinding(GraphQLSnippet):
    name = "update-binding"
    snippet = """
    mutation {
        updateBinding(input:{
            uuid: $uuid
            name: $name
            description: $description
            schedule: $schedule
            variables: $variables
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


class RemoveBinding(GraphQLSnippet):
    name = "remove-binding"
    snippet = """
    mutation {
        removeBinding(uuid: $uuid){
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


class DeployBinding(GraphQLSnippet):
    name = "deploy-binding"
    snippet = """
    mutation {
        deployBinding(uuid: $uuid){
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


class RunBinding(GraphQLSnippet):
    name = "run-binding"
    snippet = """
    mutation {
        runBinding(input:{uuid: $uuid}){
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
