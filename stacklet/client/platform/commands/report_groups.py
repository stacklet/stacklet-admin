import click

from stacklet.client.platform.executor import _run_graphql
from stacklet.client.platform.executor import StackletGraphqlExecutor, snippet_options
from stacklet.client.platform.graphql import StackletGraphqlSnippet
from stacklet.client.platform.utils import click_group_entry, default_options


@StackletGraphqlExecutor.registry.register("create-report-group")
class CreateReportGroup(StackletGraphqlSnippet):
    name = "create-report-group"
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

@StackletGraphqlExecutor.registry.register("get-report-group")
class QueryReportGroup(StackletGraphqlSnippet):
    name = "get-report-group"
    pagination = False
    snippet = """
query {
  reportGroup(name: $name) {
    id
    name
    schedule
    groupBy
    useMessageSettings
    source
    bindings
    deliverySettings {
      ... on EmailSettings {
        type
        template
        recipients {
          value
          tag
          account_owner
          resource_owner
        }
        subject
        fromEmail
        cc
        priority
        format
      }
      ... on SlackSettings {
        type
        template
        recipients {
          value
          tag
          account_owner
          resource_owner
        }
      }
      ... on JiraSettings {
        type
        template
        recipients {
          value
          tag
          account_owner
          resource_owner
        }
        summary
        project
        description
      }
    }
  }
}
"""
    required={
      "name": ""
    }

@StackletGraphqlExecutor.registry.register("list-report-groups")
class QueryReportGroups(StackletGraphqlSnippet):
    name = "list-report-groups"
    pagination = True
    snippet = """
query {
  reportGroups(
    binding: $binding
    first: $first
    last: $last
    after: $after
    before: $before
  ) {
    edges {
      node {
        id
        name
        schedule
        groupBy
        useMessageSettings
        source
        bindings
        deliverySettings {
          ... on EmailSettings {
            type
            template
            recipients {
              value
              tag
              account_owner
              resource_owner
            }
            subject
            fromEmail
            cc
            priority
            format
          }
          ... on SlackSettings {
            type
            template
            recipients {
              value
              tag
              account_owner
              resource_owner
            }
          }
          ... on JiraSettings {
            type
            template
            recipients {
              value
              tag
              account_owner
              resource_owner
            }
            summary
            project
            description
          }
        }
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
"""
    optional={
      "binding": ""
      }

@StackletGraphqlExecutor.registry.register("remove-report-group")
class RemoveReportGroup(StackletGraphqlSnippet):
    name = "remove-report-group"
    pagination = False
    snippet = """
mutation {
  removeReportGroup(name: "$name")
}
"""
    required={"name": ""}


@click.group(short_help="Run report groups queries/mutations")
@default_options()
@click.pass_context
def report_groups(*args, **kwargs):
    """
    Query against and Run mutations against Report Group objects in Stacklet

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet repository --output json list

    """
    click_group_entry(*args, **kwargs)


@report_groups.command()
@snippet_options("create-report-group")
@click.pass_context
def create(ctx, **kwargs):
    """
    Create a new or update an existing report-group
    """
    click.echo(_run_graphql(ctx=ctx, name="create-report-group", variables=kwargs))

@report_groups.command()
@snippet_options("list-report-groups")
@click.pass_context
def list(ctx, **kwargs):
    """
    Query all report-groups
    """
    click.echo(_run_graphql(ctx=ctx, name="list-report-groups", variables=kwargs))

@report_groups.command()
@snippet_options("get-report-group")
@click.pass_context
def get(ctx, **kwargs):
    """
    Query a specific report-group
    """
    click.echo(_run_graphql(ctx=ctx, name="get-report-group", variables=kwargs))

@report_groups.command()
@snippet_options("remove-report-group")
@click.pass_context
def remove(ctx, **kwargs):
    """
    Remove report-group
    """
    click.echo(_run_graphql(ctx=ctx, name="remove-report-group", variables=kwargs))
