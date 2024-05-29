import click

from stacklet.client.platform.executor import _run_graphql
from stacklet.client.platform.executor import StackletGraphqlExecutor, snippet_options
from stacklet.client.platform.graphql import StackletGraphqlSnippet
from stacklet.client.platform.utils import click_group_entry, default_options


@StackletGraphqlExecutor.registry.register("create-template")
class CreateTemplate(StackletGraphqlSnippet):
    name = "create-template"
    pagination = False
    snippet = """
mutation {
  addTemplate(input: { name: $name, content: $content }) {
    template {
      id
      name
      content
    }
  }
}
"""
    required = {"name": "", "content": ""}


@StackletGraphqlExecutor.registry.register("get-template")
class QueryTemplate(StackletGraphqlSnippet):
    name = "get-template"
    pagination = False
    snippet = """
query {
  template(name: $name) {
    id
    name
    content
  }
}
"""
    required = {"name": ""}


@StackletGraphqlExecutor.registry.register("list-templates")
class QueryTemplates(StackletGraphqlSnippet):
    name = "list-templates"
    pagination = True
    snippet = """
query {
  templates(first: $first, last: $last, before: "$before", after: "$after") {
    edges {
      node {
        id
        name
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
      total
    }
  }
}
"""


@StackletGraphqlExecutor.registry.register("remove-template")
class RemoveTemplate(StackletGraphqlSnippet):
    name = "remove-template"
    pagination = False
    snippet = """
mutation {
  removeTemplate(id: $id)
}
"""
    required = {"id": ""}


@click.group(short_help="Run templates queries/mutations")
@default_options()
@click.pass_context
def templates(*args, **kwargs):
    """
    Query against and Run mutations against Template objects in Stacklet

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet repository --output json list

    """
    click_group_entry(*args, **kwargs)


@templates.command()
@snippet_options("create-template")
@click.pass_context
def create(ctx, **kwargs):
    """
    Create a new or update an existing template
    """
    click.echo(_run_graphql(ctx=ctx, name="create-template", variables=kwargs))


@templates.command()
@snippet_options("list-templates")
@click.pass_context
def list(ctx, **kwargs):
    """
    Query all templates
    """
    click.echo(_run_graphql(ctx=ctx, name="list-templates", variables=kwargs))


@templates.command()
@snippet_options("get-template")
@click.pass_context
def get(ctx, **kwargs):
    """
    Query a specific template
    """
    click.echo(_run_graphql(ctx=ctx, name="get-template", variables=kwargs))


@templates.command()
@snippet_options("remove-template")
@click.pass_context
def remove(ctx, **kwargs):
    """
    Remove template
    """
    click.echo(_run_graphql(ctx=ctx, name="remove-template", variables=kwargs))
