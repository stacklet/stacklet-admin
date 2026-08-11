# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import logging
from pathlib import Path

import click

from . import __version__

USER_AGENT = f"stacklet.client.platform/{__version__}"

# Type for an optional boolean option. Constraining the values matters: these are sent
# on to the API, where a wrong one is a rejected mutation or a silently different
# setting rather than something the user gets told about.
BOOL_CHOICE = click.Choice(["true", "false"], case_sensitive=False)


def to_bool(value: str | None) -> bool | None:
    """
    Parse an optional boolean option, as constrained by BOOL_CHOICE.

    None has to survive as None: variables are transformed before the query is built,
    and the builder drops an option's line only when its value is None. Coercing an
    unset option to False would send it, and `autoUpdate: false` is an error on a
    dynamic policy collection rather than a no-op.
    """
    if value is None:
        return None
    return value.lower() == "true"


PAGINATION_OPTIONS = {
    "first": {
        "help": "For use with pagination. Return the first n results.",
        "default": 20,
    },
    "last": {
        "help": "For use with pagination. Return the last n results. Overrides first.",
        "default": 0,
    },
    "before": {
        "help": "For use with pagination. Return the results before a given page cursor.",
        "default": "",
    },
    "after": {
        "help": "For use with pagination. Return the results after a given page cursor.",
        "default": "",
    },
}


def expand_user_path(ctx, param, value):
    """Callback for click options to expand user paths."""
    if value is None:
        return value
    if not isinstance(value, Path):
        value = Path(value)
    return value.expanduser()


def wrap_command(func, options, required=False, prompt=False):
    for name, details in options.items():
        if not name.startswith("-"):
            name = f"--{name.replace('_', '-')}"
        if isinstance(details, str):
            click.option(
                name,
                required=required,
                help=details,
                prompt=prompt,
            )(func)
        elif isinstance(details, dict):
            click.option(
                name,
                required=required,
                prompt=prompt,
                **details,
            )(func)
        else:
            raise Exception("Options should be of type str or dict, got %s" % type(details))
    return func


def get_log_level(verbose):
    # Default to Error level (40)
    level = 40 - (verbose * 10)
    if level < 0:
        level = 0
    elif level > 50:
        level = 50
    return level


def setup_logging(level):
    logging.basicConfig()
    # Don't make botocore or urllib3 more verbose
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    root_handler = logging.getLogger()
    if level:
        root_handler.setLevel(level=get_log_level(level))
