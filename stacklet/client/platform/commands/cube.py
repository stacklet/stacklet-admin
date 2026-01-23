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

from ..context import StackletContext
from ..exceptions import MissingToken
from ..utils import get_user_agent


@click.group()
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
    data = _request(obj, "GET", "v1/meta")

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


def _run_query(context, query):
    return _request(context, "POST", "v1/load", payload={"query": query})


def _request(context: StackletContext, method: str, path: str, payload: Any = None):
    token = context.credentials.api_token()
    if not token:
        raise MissingToken()
    response = requests.request(
        method,
        url=f"{context.config.cubejs}/cubejs-api/{path}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": get_user_agent(),
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
