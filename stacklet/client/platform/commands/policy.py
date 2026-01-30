# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import Any

import click

from ..context import StackletContext
from ..exceptions import InvalidInputException
from ..graphql import GRAPHQL_SNIPPETS, StackletGraphqlSnippet
from ..graphql_cli import GraphQLCommand, register_graphql_commands, run_graphql, snippet_options


@GRAPHQL_SNIPPETS.register("list-policies")
class QueryPolicies(StackletGraphqlSnippet):
    name = "list-policies"
    snippet = """
        query {
          policies(
            first: $first
            last: $last
            before: "$before"
            after: "$after"
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
    pagination = True


@GRAPHQL_SNIPPETS.register("show-policy")
class ShowPolicy(StackletGraphqlSnippet):
    name = "show-policy"
    snippet = """
        query {
          policy(
            name: "$name"
            uuid: "$uuid"
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


@click.group(short_help="Run policy queries")
def policy(*args, **kwargs):
    """
    Manage policies
    """


def _show_policy_pre_check(context: StackletContext, cli_args: dict[str, Any]) -> dict[str, Any]:
    """Validate that either name or uuid is provided, but not both."""
    if all([cli_args.get("name"), cli_args.get("uuid")]):
        raise InvalidInputException("Either name or uuid can be set, but not both")
    if not any([cli_args.get("name"), cli_args.get("uuid")]):
        raise InvalidInputException("Either name or uuid must be set")
    return cli_args


register_graphql_commands(
    policy,
    [
        GraphQLCommand("list", "list-policies", "List policies in Stacklet"),
        GraphQLCommand(
            "show",
            "show-policy",
            "Show policy in Stacklet by either name or uuid",
            pre_check=_show_policy_pre_check,
        ),
    ],
)


@policy.command()
@snippet_options("show-policy")
@click.pass_obj
def show_source(obj, **kwargs):
    """
    Show policy source in Stacklet by either name or uuid
    """
    _show_policy_pre_check(obj, kwargs)
    click.echo(
        run_graphql(obj, name="show-policy", variables=kwargs, raw=True)["data"]["policy"][
            "sourceYAML"
        ]
    )
