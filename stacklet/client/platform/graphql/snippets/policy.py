# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from ..snippet import GraphQLSnippet


class ListPolicies(GraphQLSnippet):
    name = "list-policies"
    snippet = """
        query {
          policies(
            first: $first
            last: $last
            before: $before
            after: $after
          ) {
            edges {
              node {
                id
                uuid
                version
                name
                description
                category
                compliance
                severity
                resourceType
                provider
                resource
                mode
                tags {
                 key
                  value
                }
                commit {
                    hash
                    author
                    msg
                }
                repository {
                    id
                    url
                    name
                }
                path
                source
                validationError
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
    pagination_expr = "data.policies.pageInfo"
    result_expr = "data.policies.edges[].node"


class ShowPolicy(GraphQLSnippet):
    name = "show-policy"
    snippet = """
        query {
          policy(
            name: $name
            uuid: $uuid
          ) {
            id
            uuid
            version
            name
            description
            category
            compliance
            severity
            resourceType
            provider
            resource
            mode
            tags {
              key
              value
            }
            commit {
                hash
                author
                msg
            }
            repository {
                id
                url
                name
            }
            path
            source
            sourceYAML
            lastExecution {
              id
              uuid
              account {
                id
                key
                name
                path
                email
                status
                status_message
                validated_at
              }
              start
              end
              status
              issues
              metricResources
              metricDuration
              metricApiCalls
              metricException
              metricRateLimitExceeded
              paramCache
              paramRegion
              paramDryrun
              runner
            }
          }
      }
    """
    optional = {
        "name": "Policy Name",
        "uuid": "Policy UUID",
    }
