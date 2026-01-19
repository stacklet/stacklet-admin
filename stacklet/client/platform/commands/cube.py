# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import io
import json
import sys
import textwrap
from datetime import datetime
from pprint import pformat

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
    data = _get(ctx, "v1/meta")

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
    context = StackletContext(ctx.obj["config"], ctx.obj["raw_config"])
    token = get_token()

    url = f"https://{context.config.cubejs}/cubejs-api/v1/load"

    data = {"query": query}
    response = requests.post(
        url=url,
        headers={"Authorization": token, "Content-Type": "application/json"},
        data=json.dumps(data),
    )
    return response.json()


def _get(ctx, path: str):
    context = StackletContext(ctx.obj["config"], ctx.obj["raw_config"])
    token = get_token()

    url = f"https://{context.config.cubejs}/cubejs-api/{path}"

    response = requests.get(
        url=url,
        headers={"Authorization": token, "Content-Type": "application/json"},
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
