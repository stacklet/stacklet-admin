# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from ..snippet import GraphQLSnippet


class ListAccountGroups(GraphQLSnippet):
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


class AddAccountGroup(GraphQLSnippet):
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


class UpdateAccountGroup(GraphQLSnippet):
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


class ShowAccountGroup(GraphQLSnippet):
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


class RemoveAccountGroup(GraphQLSnippet):
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


class AddAccountGroupItem(GraphQLSnippet):
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


class RemoveAccountGroupItem(GraphQLSnippet):
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
