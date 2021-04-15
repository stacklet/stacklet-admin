import click

from cli.executor import StackletGraphqlExecutor, _run_graphql, snippet_options
from cli.graphql import StackletGraphqlSnippet
from cli.utils import click_group_entry, default_options


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
        status
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


@click.group()
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
