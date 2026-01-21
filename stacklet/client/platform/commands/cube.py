# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import io
import json
import sys
import textwrap
from datetime import datetime
from pprint import pformat
from typing import Any

import click
import requests

from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.utils import click_group_entry, default_options, get_token


@click.group()
@default_options()
@click.pass_context
def cubejs(*args, **kwargs):
    """
    Run arbitrary cubejs queries
    """
    click_group_entry(*args, **kwargs)


@cubejs.command()
@click.option("--query", help="Graphql Query or Mutation", default=sys.stdin)
@click.pass_context
def run(ctx, query):
    if isinstance(query, io.IOBase):
        query = query.read()

    response = _run_query(ctx, json.loads(query))
    click.echo(pformat(response))


@cubejs.command()
@click.pass_context
def meta(ctx):
    data = _request(ctx, "GET", "v1/meta")

    cubes = {cube["name"]: cube for cube in data["cubes"]}
    for name in sorted(cubes):
        value = cubes[name]
        value.pop("name")
        click.echo(f"{name}:\n{textwrap.indent(pformat(value), '    ')}\n")


@cubejs.command()
@click.pass_context
def resource_counts(ctx):
    response = _run_query(ctx, _resource_counts)
    data = response["data"]
    for row in data:
        date = datetime.fromisoformat(row["ResourceCounts.date"])
        count = row["ResourceCounts.count"]
        click.echo(f"{date.date().isoformat()}: {count}")


def _run_query(ctx, query):
    return _request(ctx, "POST", "v1/load", payload={"query": query})


def _request(ctx, method: str, path: str, payload: Any = None):
    context = StackletContext(ctx.obj["config"], ctx.obj["raw_config"])
    token = get_token()
    response = requests.request(
        method,
        url=f"{context.config.cubejs}/cubejs-api/{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    return response.json()


_resource_counts = {
    "measures": ["ResourceCounts.count"],
    "timeDimensions": [
        {
            "dimension": "ResourceCounts.date",
            "granularity": "day",
            "dateRange": "Last 30 days",
        }
    ],
    "order": [["ResourceCounts.date", "desc"]],
    "dimensions": [],
}
