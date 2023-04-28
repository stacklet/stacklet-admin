import click
import json

from stacklet.client.platform.executor import _run_graphql
from stacklet.client.platform.executor import StackletGraphqlExecutor, snippet_options
from stacklet.client.platform.graphql import StackletGraphqlSnippet
from stacklet.client.platform.utils import click_group_entry, default_options


@StackletGraphqlExecutor.registry.register("list-accounts")
class ListAccountsSnippet(StackletGraphqlSnippet):
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


@StackletGraphqlExecutor.registry.register("show-account")
class QueryAccountSnippet(StackletGraphqlSnippet):
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


@StackletGraphqlExecutor.registry.register("update-account")
class UpdateAccountSnippet(StackletGraphqlSnippet):
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


@StackletGraphqlExecutor.registry.register("add-account")
class AddAccountSnippet(StackletGraphqlSnippet):
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


@StackletGraphqlExecutor.registry.register("remove-account")
class RemoveAccountSnippet(StackletGraphqlSnippet):
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


@StackletGraphqlExecutor.registry.register("validate-account")
class ValidateAccountSnippet(StackletGraphqlSnippet):
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


@click.group(short_help="Run account queries/mutations")
@default_options()
@click.pass_context
def account(*args, **kwargs):
    """
    Query against and Run mutations against Account objects in Stacklet.

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet account --output json list

    """
    click_group_entry(*args, **kwargs)


@account.command()
@snippet_options("list-accounts")
@click.pass_context
def list(ctx, **kwargs):
    """
    List cloud accounts in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="list-accounts", variables=kwargs))


@account.command()
@snippet_options("add-account")
@click.pass_context
def add(ctx, **kwargs):
    """
    Add an account to Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="add-account", variables=kwargs))


@account.command()
@snippet_options("remove-account")
@click.pass_context
def remove(ctx, **kwargs):
    """
    Remove an account from Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="remove-account", variables=kwargs))


@account.command()
@snippet_options("update-account")
@click.pass_context
def update(ctx, **kwargs):
    """
    Update an account in platform
    """
    click.echo(_run_graphql(ctx=ctx, name="update-account", variables=kwargs))


@account.command()
@snippet_options("show-account")
@click.pass_context
def show(ctx, **kwargs):
    """
    Show an account in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="show-account", variables=kwargs))


@account.command()
@snippet_options("validate-account")
@click.pass_context
def validate(ctx, **kwargs):
    """
    Validate an account in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="validate-account", variables=kwargs))


@account.command()
@snippet_options("list-accounts")
@click.pass_context
def validate_all(ctx, **kwargs):
    """
    Validate all accounts in Stacklet
    """
    result = _run_graphql(ctx=ctx, name="list-accounts", variables=kwargs, raw=True)

    # get all the accounts
    count = result["data"]["accounts"]["pageInfo"]["total"]
    kwargs["last"] = count

    result = _run_graphql(ctx=ctx, name="list-accounts", variables=kwargs, raw=True)
    account_provider_pairs = [
        {"provider": r["node"]["provider"], "key": r["node"]["key"]}
        for r in result["data"]["accounts"]["edges"]
    ]
    for pair in account_provider_pairs:
        click.echo(_run_graphql(ctx=ctx, name="validate-account", variables=pair))
