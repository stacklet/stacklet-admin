import click

from cli.executor import (StackletFragmentExecutor, _run_fragment,
                          fragment_options)
from cli.utils import default_options
from cli.fragments import StackletFragment


@StackletFragmentExecutor.registry.register("list-accounts")
class QueryAccountFragment(StackletFragment):
    name = "list-accounts"
    fragment = """
        query {
            accounts {
                edges {
                    node {
                        name
                        id
                        key
                        provider
                        path
                        securityContext
                    }
                }
            }
        }
    """
    required = {}


@StackletFragmentExecutor.registry.register("add-account")
class AddAccountFragment(StackletFragment):
    name = "add-account"
    fragment = """
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
def account(ctx, config, output):
    """
    Query against and Run mutations against Account objects in Stacklet.

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet accounts --output json list

    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["output"] = output


@account.command()
@fragment_options("list-accounts")
@click.pass_context
def list(ctx):
    """
    List cloud accounts in Stacklet
    """
    click.echo(_run_fragment(ctx=ctx, name="list-accounts", variables=None))


@account.command()
@fragment_options("add-account")
@click.pass_context
def add(ctx, **kwargs):
    """
    Add an account to Stacklet
    """
    click.echo(_run_fragment(ctx=ctx, name="add-account", variables=dict(**kwargs)))
