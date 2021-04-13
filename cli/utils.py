import click
import os

from cli.context import StackletContext
from cli.formatter import Formatter


_DEFAULT_OPTIONS = [
    click.option("--config", default=StackletContext.DEFAULT_CONFIG, help='Config File Location'),
    click.option(
        "--output",
        type=click.Choice(list(Formatter.registry.keys()), case_sensitive=False),
        default=StackletContext.DEFAULT_OUTPUT,
        help='Ouput type'
    )
]


def get_token():
    with open(
        os.path.expanduser(StackletContext.DEFAULT_CREDENTIALS), "r"
    ) as f:  # noqa
        token = f.read()
    return token


def default_options(*args, **kwargs):
    def wrapper(func):
        for o in _DEFAULT_OPTIONS:
            o(func)
        return func
    return wrapper
