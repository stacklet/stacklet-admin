# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import logging

import click

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
