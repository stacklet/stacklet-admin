import logging
import os

import click
from .context import StackletContext
from .formatter import Formatter

_DEFAULT_OPTIONS = {
    "config": {"default": "", "help": ""},
    "output": {
        "type": click.Choice(list(Formatter.registry.keys()), case_sensitive=False),
        "default": "",
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
        "help": "For use with pagination. Return the last n results.",
        "default": 20,
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
            name = f'--{name.replace("_", "-")}'
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
            raise Exception(
                "Options should be of type str or dict, got %s" % type(details)
            )
    return func


def get_token():
    with open(os.path.expanduser(StackletContext.DEFAULT_CREDENTIALS), "r") as f:
        token = f.read()
    return token


def default_options(*args, **kwargs):
    def wrapper(func):
        wrap_command(func, _DEFAULT_OPTIONS, required=False, prompt=False)
        return func

    return wrapper


def get_log_level(verbose):
    level = 50 - (verbose * 10)
    if level < 0:
        level = 0
    elif level > 50:
        level = 50
    return level


def click_group_entry(
    ctx,
    config,
    output,
    cognito_user_pool_id,
    cognito_client_id,
    cognito_region,
    api,
    v,
):
    logging.basicConfig()
    root_handler = logging.getLogger()
    if v != 0:
        root_handler.setLevel(level=get_log_level(v))

    ctx.ensure_object(dict)
    config_items = [cognito_user_pool_id, cognito_client_id, cognito_region, api]
    if any(config_items) and not all(config_items):
        raise Exception(
            "All options must be set for config items: --cognito-user-pool-id, "
            + "--cognito-client-id, --cognito-region, and --api"
        )
    # inherit the parent's configs if they exist
    ctx.obj.setdefault("config", ctx.obj.get("config", StackletContext.DEFAULT_CONFIG))
    ctx.obj.setdefault("output", ctx.obj.get("output", StackletContext.DEFAULT_OUTPUT))
    ctx.obj.setdefault("raw_config", ctx.obj.get("raw_config", {}))
    if config:
        ctx.obj["config"] = config
    if output:
        ctx.obj["output"] = output
    if all(config_items):
        ctx.obj["raw_config"] = {
            "cognito_user_pool_id": cognito_user_pool_id,
            "cognito_client_id": cognito_client_id,
            "region": cognito_region,
            "api": api,
        }
