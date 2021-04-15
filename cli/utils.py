import logging
import os

import click

from cli.context import StackletContext
from cli.formatter import Formatter

_DEFAULT_OPTIONS = [
    click.option(
        "--config", default=StackletContext.DEFAULT_CONFIG, help="Config File Location"
    ),
    click.option(
        "--output",
        type=click.Choice(list(Formatter.registry.keys()), case_sensitive=False),
        default=StackletContext.DEFAULT_OUTPUT,
        help="Ouput type",
    ),
    click.option(
        "--cognito-user-pool-id",
        default="",
        help=(
            "If set, --cognito-user-pool-id, --cognito-client-id, "
            "--cognito-region, and --api must also be set."
        ),
    ),
    click.option(
        "--cognito-client-id",
        default="",
        help=(
            "If set, --cognito-user-pool-id, --cognito-client-id, "
            "--cognito-region, and --api must also be set."
        ),
    ),
    click.option(
        "--cognito-region",
        default="",
        help=(
            "If set, --cognito-user-pool-id, --cognito-client-id, "
            "--cognito-region, and --api must also be set."
        ),
    ),
    click.option(
        "--api",
        default="",
        help=(
            "If set, --cognito-user-pool-id, --cognito-client-id, "
            "--cognito-region, and --api must also be set."
        ),
    ),
    click.option(
        "--first",
        default="20",
        help="For use with pagination.",
    ),
    click.option(
        "--last",
        default="20",
        help="For use with pagination.",
    ),
    click.option(
        "--before",
        default="",
        help="For use with pagination.",
    ),
    click.option(
        "--after",
        default="",
        help="For use with pagination.",
    ),
    click.option(
        "-v",
        "--verbose",
        default=0,
        count=True,
        help="Verbosity level, increase verbosity by appending v, e.g. -vvv",
    ),
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
    first,
    last,
    before,
    after,
    verbose,
):
    logging.basicConfig(level=get_log_level(verbose))
    ctx.ensure_object(dict)
    config_items = [cognito_user_pool_id, cognito_client_id, cognito_region, api]
    if any(config_items) and not all(config_items):
        raise Exception(
            "All options must be set for config items: --cognito-user-pool-id, "
            + "--cognito-client-id, --cognito-region, and --api"
        )
    ctx.obj["config"] = config
    ctx.obj["output"] = output
    ctx.obj["page_variables"] = {
        "first": first,
        "last": last,
        "before": before,
        "after": after,
    }
    ctx.obj["raw_config"] = {
        "cognito_user_pool_id": cognito_user_pool_id,
        "cognito_client_id": cognito_client_id,
        "region": cognito_region,
        "api": api,
    }
