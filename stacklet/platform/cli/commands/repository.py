import click
from stacklet.platform.cli.executor import _run_graphql
from stacklet.platform.cli.executor import StackletGraphqlExecutor, snippet_options
from stacklet.platform.cli.graphql import StackletGraphqlSnippet
from stacklet.platform.cli.utils import click_group_entry, default_options


@StackletGraphqlExecutor.registry.register("add-repository")
class AddRepositorySnippet(StackletGraphqlSnippet):
    name = "add-repository"
    snippet = """
    mutation {
      addRepository(
        input: {
          url: "$url"
          name: "$name"
        }
      ) {
        repository {
            url
            name
        }
      }
    }
    """
    required = {
        "url": "Policy Repository URL",
        "name": "Human Readable Policy Repository Name",
    }


@StackletGraphqlExecutor.registry.register("process-repository")
class ProcessRepositorySnippet(StackletGraphqlSnippet):
    name = "process-repository"
    snippet = """
    mutation {
      processRepository(input:{url: "$url"}) {
        status
      }
    }
    """
    required = {"url": "Repository URL to process"}


@StackletGraphqlExecutor.registry.register("list-repository")
class ListRepositorySnippet(StackletGraphqlSnippet):
    name = "list-repository"
    snippet = """
    {
        repositories {
        edges {
          node {
            id
            name
            url
            policyFileSuffix
            policyDirectories
            branchName
            authUser
            sshPublicKey
            head
            lastScanned
            provider
          }
        }
      }
    }
    """


@StackletGraphqlExecutor.registry.register("remove-repository")
class RemoveRepositorySnippet(StackletGraphqlSnippet):
    name = "remove-repository"
    snippet = """
    mutation {
      removeRepository(
          url: "$url"
      ) {
        repository {
            url
            name
        }
      }
    }
    """
    required = {
        "url": "Policy Repository URL",
    }


@click.group(short_help="Run repository queries/mutations")
@default_options()
@click.pass_context
def repository(*args, **kwargs):
    """
    Query against and Run mutations against Repository objects in Stacklet

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet accounts --output json list

    """
    click_group_entry(*args, **kwargs)


@repository.command()
@snippet_options("add-repository")
@click.pass_context
def add(ctx, **kwargs):
    """
    Add a Policy Repository to Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="add-repository", variables=kwargs))


@repository.command()
@snippet_options("process-repository")
@click.pass_context
def process(ctx, **kwargs):
    """
    Process a Policy Repository in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="process-repository", variables=kwargs))


@repository.command()
@snippet_options("list-repository")
@click.pass_context
def list(ctx, **kwargs):
    """
    List repositories
    """
    click.echo(_run_graphql(ctx=ctx, name="list-repository", variables=kwargs))


@repository.command()
@snippet_options("remove-repository")
@click.pass_context
def remove(ctx, **kwargs):
    """
    Remove a Policy Repository to Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="remove-repository", variables=kwargs))
