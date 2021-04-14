import click

from cli.executor import StackletGraphqlExecutor, _run_graphql, snippet_options
from cli.graphql import StackletGraphqlSnippet
from cli.utils import click_group_entry, default_options


@StackletGraphqlExecutor.registry.register("list-accounts")
class QueryAccountFragment(StackletGraphqlSnippet):
    name = "list-accounts"
    snippet = """
        query {
          accounts(
            provider: AWS
            first: $first
            last: $last
            before: "$before"
            after: "$after"
          ) {
            edges {
              node {
                key
                id
                name
                email
                provider
                path
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


@StackletGraphqlExecutor.registry.register("add-account")
class AddAccountFragment(StackletGraphqlSnippet):
    name = "add-account"
    snippet = """
    mutation {
      addAccount(input:{
        provider: AWS,
        key:"$key",
        name:"$name",
        path:"$path",
        email:"$email",
        securityContext:"$security_context"
      }){
        status
      }
    }
    """
    required = {
        "key": "Account Key in Stacklet, e.g. Account ID in AWS",
        "name": "Account Name in Stacklet",
        "path": "Account Path",
        "email": "Account Email Address",
        "security_context": "Role for Custodian policy execution",
    }


@click.group()
@default_options()
@click.pass_context
def account(*args, **kwargs):
    """
    Query against and Run mutations against Account objects in Stacklet.

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet accounts --output json list

    """
    click_group_entry(*args, **kwargs)


@account.command()
@snippet_options("list-accounts")
@click.pass_context
def list(ctx):
    """
    List cloud accounts in Stacklet
    """
    click.echo(
        _run_graphql(ctx=ctx, name="list-accounts", variables=ctx.obj["page_variables"])
    )


@account.command()
@snippet_options("add-account")
@click.pass_context
def add(ctx, **kwargs):
    """
    Add an account to Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="add-account", variables=dict(**kwargs)))
