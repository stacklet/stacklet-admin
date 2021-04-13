import click
import io
import sys

from cli.utils import default_options
from cli.executor import _run_fragment
from cli.fragments import StackletFragment


@click.group()
@default_options()
@click.pass_context
def fragment(ctx, config, output):
    """
    Run arbitrary fragments
    """
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["output"] = output


@fragment.command()
@click.option('--fragment', help='', default=sys.stdin)
@click.pass_context
def run(ctx, fragment):
    if isinstance(fragment, io.IOBase):
        fragment = fragment.read()
    stacklet_fragment = StackletFragment(
        name='adhoc',
        fragment=fragment
    )
    click.echo(_run_fragment(ctx=ctx, name=None, variables=None, fragment=stacklet_fragment))
