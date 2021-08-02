import click

from stacklet.platform.cli.executor import _run_graphql
from stacklet.platform.cli.executor import StackletGraphqlExecutor, snippet_options
from stacklet.platform.cli.graphql import StackletGraphqlSnippet
from stacklet.platform.cli.utils import click_group_entry, default_options


@StackletGraphqlExecutor.registry.register("list-policy-collections")
class QueryPolicyCollectionSnippet(StackletGraphqlSnippet):
    name = "list-policy-collections"
    snippet = """
        query {
          policyCollections(
            first: $first
            last: $last
            before: "$before"
            after: "$after"
          ) {
            edges {
              node {
                id
                uuid
                name
                description
                provider
                repository
                itemCount
                items {
                    uuid
                    name
                    version
                }
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


@StackletGraphqlExecutor.registry.register("show-policy-collection")
class ShowPolicyCollection(StackletGraphqlSnippet):
    name = "show-policy-collection"
    snippet = """
        query {
          policyCollection(
            uuid: "$uuid"
          ) {
            id
            uuid
            name
            description
            provider
            repository
            itemCount
            items {
                uuid
                name
                version
            }
          }
      }
    """
    required = {"uuid": "Policy Collection UUID"}


@StackletGraphqlExecutor.registry.register("add-policy-collection")
class AddPolicyCollection(StackletGraphqlSnippet):
    name = "add-policy-collection"
    snippet = """
    mutation {
      addPolicyCollection(input:{
        name: "$name"
        provider: $provider
        description: "$description"
      }){
        collection {
            id
            uuid
            name
            description
            provider
            repository
            itemCount
            items {
                uuid
                name
                version
            }
        }
      }
    }
    """
    required = {
        "name": "Policy Collection Name in Stacklet",
        "provider": "Cloud Provider",
    }

    optional = {
        "description": "Policy Collection Description",
    }


@StackletGraphqlExecutor.registry.register("update-policy-collection")
class UpdatePolicyCollection(StackletGraphqlSnippet):
    name = "update-policy-collection"
    snippet = """
    mutation {
      updatePolicyCollection(input:{
        uuid: "$uuid"
        name: "$name"
        provider: $provider
        description: "$description"
      }){
        collection {
            id
            uuid
            name
            description
            provider
            repository
            itemCount
            items {
                uuid
                name
                version
            }
        }
      }
    }
    """
    required = {"uuid": "Policy Collection UUID"}

    optional = {
        "name": "Policy Collection Name in Stacklet",
        "provider": "Cloud Provider",
        "description": "Policy Collection Description",
    }


@StackletGraphqlExecutor.registry.register("add-policy-collection-item")
class AddPolicyCollectionItem(StackletGraphqlSnippet):
    name = "add-policy-collection-item"
    snippet = """
        mutation {
          addPolicyCollectionItems(input:{
            uuid: "$uuid"
            items: [
                {
                    policyUUID: "$policy_uuid"
                    policyVersion: $policy_version
                }
            ]
          }) {
              collection {
                id
                uuid
                name
                description
                provider
                repository
                itemCount
                items {
                    uuid
                    name
                    version
                }
            }
          }
      }
    """
    required = {
        "uuid": "Account group UUID",
        "policy_uuid": "Policy UUID",
    }

    optional = {"policy_version": "Policy Version"}


@StackletGraphqlExecutor.registry.register("remove-policy-collection-item")
class RemovePolicyCollectionItem(StackletGraphqlSnippet):
    name = "remove-policy-collection-item"
    snippet = """
        mutation {
          removePolicyCollectionItems(input:{
            uuid: "$uuid"
            items: [
                {
                    policyUUID: "$policy_uuid"
                    policyVersion: $policy_version
                }
            ]
          }) {
              collection {
                id
                uuid
                name
                description
                provider
                repository
                itemCount
                items {
                    uuid
                    name
                    version
                }
            }
          }
      }
    """
    required = {
        "uuid": "Account group UUID",
        "policy_uuid": "Policy UUID",
    }

    optional = {"policy_version": "Policy Version"}


@StackletGraphqlExecutor.registry.register("remove-policy-collection")
class RemovePolicyCollection(StackletGraphqlSnippet):
    name = "remove-policy-collection"
    snippet = """
    mutation {
      removePolicyCollection(
        uuid: "$uuid"
      ){
        collection {
            id
            uuid
            name
            description
            provider
            repository
            itemCount
            items {
                uuid
                name
                version
            }
        }
      }
    }
    """
    required = {"uuid": "Policy Collection UUID"}


@click.group(short_help="Run policy collection queries/mutations")
@default_options()
@click.pass_context
def policy_collection(*args, **kwargs):
    click_group_entry(*args, **kwargs)


@policy_collection.command()
@snippet_options("list-policy-collections")
@click.pass_context
def list(ctx, **kwargs):
    """
    List policy collections in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="list-policy-collections", variables=kwargs))


@policy_collection.command()
@snippet_options("add-policy-collection")
@click.pass_context
def add(ctx, **kwargs):
    """
    Add policy collection in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="add-policy-collection", variables=kwargs))


@policy_collection.command()
@snippet_options("show-policy-collection")
@click.pass_context
def show(ctx, **kwargs):
    """
    Show policy collection in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="show-policy-collection", variables=kwargs))


@policy_collection.command()
@snippet_options("update-policy-collection")
@click.pass_context
def update(ctx, **kwargs):
    """
    Update policy collection in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="update-policy-collection", variables=kwargs))


@policy_collection.command()
@snippet_options("add-policy-collection-item")
@click.pass_context
def add_item(ctx, **kwargs):
    """
    Add item to policy collection in Stacklet
    """
    click.echo(
        _run_graphql(ctx=ctx, name="add-policy-collection-item", variables=kwargs)
    )


@policy_collection.command()
@snippet_options("remove-policy-collection")
@click.pass_context
def remove(ctx, **kwargs):
    """
    Remove policy collection in Stacklet
    """
    click.echo(_run_graphql(ctx=ctx, name="remove-policy-collection", variables=kwargs))


@policy_collection.command()
@snippet_options("remove-policy-collection-item")
@click.pass_context
def remove_item(ctx, **kwargs):
    """
    Remove item from a policy collection in Stacklet
    """
    click.echo(
        _run_graphql(ctx=ctx, name="remove-policy-collection-item", variables=kwargs)
    )
