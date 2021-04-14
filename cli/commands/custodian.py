import click
import sys

from c7n import cli as c7n_cli


class CustodianCommand(click.Command):
    """
    Bridge Custodian's argparse cli with click
    """

    def parse_args(self, ctx, args):
        # because we're running this in the stacklet cli, we need to shift the args
        # over by one index, then run custodian's index over by invoking the c7n cli
        # main entrypoint:
        #
        # example:
        #
        #   $ custodian run policy.yaml -s output
        #   $ stacklet custodian run policy.yaml -s output
        sys.argv = sys.argv[1:]
        c7n_cli.main()
