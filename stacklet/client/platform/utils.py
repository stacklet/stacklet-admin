# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import logging

import click

from .config import DEFAULT_CONFIG_FILE, DEFAULT_OUTPUT_FORMAT
from .formatter import Formatter

_DEFAULT_OPTIONS = {
    "config": {"default": DEFAULT_CONFIG_FILE, "help": "Configuration file"},
    "output": {
        "type": click.Choice(list(Formatter.registry.keys()), case_sensitive=False),
        "default": DEFAULT_OUTPUT_FORMAT,
        "help": "Output type",
    },
    "cognito_user_pool_id": {
        "help": (
            "If set, --cognito-user-pool-id, --cognito-client-id, "
            "--cognito-region, and --api must also be set."
        )
    },
    "cognito_client_id": {
        "help": (
            "If set, --cognito-user-pool-id, --cognito-client-id, "
            "--cognito-region, and --api must also be set."
        )
    },
    "cognito_region": {
        "help": (
            "If set, --cognito-user-pool-id, --cognito-client-id, "
            "--cognito-region, and --api must also be set."
        )
    },
    "api": {
        "help": (
            "If set, --cognito-user-pool-id, --cognito-client-id, "
            "--cognito-region, and --api must also be set."
        )
    },
    "-v": {
        "count": True,
        "default": 0,
        "help": "Verbosity level, increase verbosity by appending v, e.g. -vvv",
    },
}

_PAGINATION_OPTIONS = {
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
        "help": "For use with pagination. Return the results after a given page curosr.",
        "default": "",
    },
}


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


def default_options(*args, **kwargs):
    def wrapper(func):
        wrap_command(func, _DEFAULT_OPTIONS, required=False, prompt=False)
        return func

    return wrapper


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
