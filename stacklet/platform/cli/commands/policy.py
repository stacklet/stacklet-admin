import click

from stacklet.platform.cli.exceptions import InvalidInputException
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
    """
    optional = {
        "name": "Policy Name",
        "uuid": "Policy UUID",
    }


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


def check_show_input(kwargs):
    if all([kwargs["name"], kwargs["uuid"]]):
        raise InvalidInputException("Either name or uuid can be set, but not both")
    if not any([kwargs["name"], kwargs["uuid"]]):
        raise InvalidInputException("Either name or uuid must be set")


@policy.command()
@snippet_options("show-policy")
@click.pass_context
def show(ctx, **kwargs):
    """
    Show policy in Stacklet by either name or uuid
    """
    check_show_input(kwargs)
    click.echo(_run_graphql(ctx=ctx, name="show-policy", variables=kwargs))


@policy.command()
@snippet_options("show-policy")
@click.pass_context
def show_source(ctx, **kwargs):
    """
    Show policy source in Stacklet by either name or uuid
    """
    check_show_input(kwargs)
    click.echo(
        _run_graphql(ctx=ctx, name="show-policy", variables=kwargs, raw=True)["data"][
            "policy"
        ]["sourceYAML"]
    )
