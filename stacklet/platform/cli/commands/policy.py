import click

from stacklet.platform.cli.executor import _run_graphql
from stacklet.platform.cli.executor import StackletGraphqlExecutor, snippet_options
from stacklet.platform.cli.graphql import StackletGraphqlSnippet
from stacklet.platform.cli.utils import click_group_entry, default_options


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
                execMode
                tags
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
              }
            }
            pageInfo {
              hasPreviousPage
              hasNextPage
              startCursor
              endCursor
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
            execMode
            tags
            commit
            repository
            path
            source
            sourceYAML
          }
      }
    """
    required = {"name": "Policy Name"}


@click.group(short_help="Run policy queries")
@default_options()
@click.pass_context
def policy(*args, **kwargs):
    click_group_entry(*args, **kwargs)


@policy.command()
@snippet_options("list-policies")
@click.pass_context
def list(ctx, **kwargs):
    """
    List policies in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="list-policies", variables=kwargs))


@policy.command()
@snippet_options("show-policy")
@click.pass_context
def show(ctx, **kwargs):
    """
    Show policy in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="show-policy", variables=kwargs))
