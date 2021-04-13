import click

from cli.executor import (StackletFragmentExecutor, _run_fragment,
                          fragment_options)
from cli.fragments import StackletFragment
from cli.utils import default_options


@StackletFragmentExecutor.registry.register("add-repository")
class AddRepositoryFragment(StackletFragment):
    name = "add-repository"
    fragment = """
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


@StackletFragmentExecutor.registry.register("process-repository")
class ProcessRepositoryFragment(StackletFragment):
    name = "process-repository"
    fragment = """
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
def repository(ctx, config, output):
    """
    Query against and Run mutations against Repository objects in Stacklet

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet accounts --output json list

    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["output"] = output


@repository.command()
@fragment_options("add-repository")
@click.pass_context
def add(ctx, **kwargs):
    """
    Add a Policy Repository to Stacklet
    """
    click.echo(_run_fragment(ctx=ctx, name="add-repository", variables=dict(**kwargs)))
