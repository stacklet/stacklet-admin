# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json

from ..snippet import GraphQLSnippet


class ListAccounts(GraphQLSnippet):
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


class ShowAccount(GraphQLSnippet):
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


class UpdateAccount(GraphQLSnippet):
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


class AddAccount(GraphQLSnippet):
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


class RemoveAccount(GraphQLSnippet):
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


class ValidateAccount(GraphQLSnippet):
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
