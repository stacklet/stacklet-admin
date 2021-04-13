import os

from cli.context import StackletContext


def get_token():
    with open(
        os.path.expanduser(StackletContext.DEFAULT_CREDENTIALS), "r"
    ) as f:  # noqa
        token = f.read()
    return token
