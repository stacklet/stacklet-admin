# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click

from stacklet.client.platform.exceptions import InvalidInputException
from stacklet.client.platform.executor import StackletGraphqlExecutor, _run_graphql, snippet_options
from stacklet.client.platform.graphql import StackletGraphqlSnippet
from stacklet.client.platform.utils import default_options


@StackletGraphqlExecutor.registry.register("list-policies")
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


@StackletGraphqlExecutor.registry.register("show-policy")
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
@default_options()
def policy(*args, **kwargs):
    """
    Manage policies
    """


@policy.command()
@snippet_options("list-policies")
@click.pass_obj
def list(obj, **kwargs):
    """
    List policies in Stacklet
    """
    click.echo(_run_graphql(obj, name="list-policies", variables=kwargs))


def check_show_input(kwargs):
    if all([kwargs["name"], kwargs["uuid"]]):
        raise InvalidInputException("Either name or uuid can be set, but not both")
    if not any([kwargs["name"], kwargs["uuid"]]):
        raise InvalidInputException("Either name or uuid must be set")


@policy.command()
@snippet_options("show-policy")
@click.pass_obj
def show(obj, **kwargs):
    """
    Show policy in Stacklet by either name or uuid
    """
    check_show_input(kwargs)
    click.echo(_run_graphql(obj, name="show-policy", variables=kwargs))


@policy.command()
@snippet_options("show-policy")
@click.pass_obj
def show_source(obj, **kwargs):
    """
    Show policy source in Stacklet by either name or uuid
    """
    check_show_input(kwargs)
    click.echo(
        _run_graphql(obj, name="show-policy", variables=kwargs, raw=True)["data"]["policy"][
            "sourceYAML"
        ]
    )
