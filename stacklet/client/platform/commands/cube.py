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

from ..context import StackletContext
from ..utils import default_options


@click.group()
@default_options()
def cubejs(*args, **kwargs):
    """
    Run arbitrary cubejs queries
    """


@cubejs.command()
@click.option("--query", help="Graphql Query or Mutation", default=sys.stdin)
@click.pass_obj
def run(obj, query):
    if isinstance(query, io.IOBase):
        query = query.read()

    response = _run_query(obj, json.loads(query))
    click.echo(pformat(response))


@cubejs.command()
@click.pass_obj
def meta(obj):
    data = _get(obj, "v1/meta")

    cubes = {cube["name"]: cube for cube in data["cubes"]}
    for name in sorted(cubes):
        value = cubes[name]
        value.pop("name")
        click.echo(f"{name}:\n{textwrap.indent(pformat(value), '    ')}\n")


@cubejs.command()
@click.pass_obj
def resource_counts(obj):
    response = _run_query(obj, _resource_counts)
    data = response["data"]
    for row in data:
        date = datetime.fromisoformat(row["ResourceCounts.date"])
        count = row["ResourceCounts.count"]
        click.echo(f"{date.date().isoformat()}: {count}")


def _run_query(context: StackletContext, query):
    token = context.credentials.api_token()

    url = f"https://{context.config.cubejs}/cubejs-api/v1/load"

    data = {"query": query}
    response = requests.post(
        url=url,
        headers={"Authorization": token, "Content-Type": "application/json"},
        data=json.dumps(data),
    )
    return response.json()


def _get(context: StackletContext, path: str):
    token = context.credentials.api_token()

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
