# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import logging

import requests

from .context import StackletContext
from .exceptions import MissingToken
from .registry import PluginRegistry
from .utils import PAGINATION_OPTIONS, get_user_agent, wrap_command


class StackletGraphqlExecutor:
    """
    Execute Graphql against the API
    """

    registry = PluginRegistry("StackletGraphqlSnippets")

    def __init__(self, context: StackletContext):
        token = context.credentials.api_token()
        if not token:
            raise MissingToken()

        self.api = context.config.api
        self.log = logging.getLogger("StackletGraphqlExecutor")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "User-Agent": get_user_agent(),
            }
        )

    def run(self, snippet, variables=None):
        if variables is None:
            variables = {}
        request = snippet.build(variables)
        self.log.debug("Request: %s" % json.dumps(request, indent=2))
        res = self.session.post(self.api, json=request)
        self.log.debug("Response: %s" % json.dumps(res.json(), indent=2))
        return res.json()


def snippet_options(*args, **kwargs):
    snippet_name = args[0]
    snippet = StackletGraphqlExecutor.registry.get(snippet_name)

    def wrapper(func):
        if not snippet:
            return func
        func = wrap_command(func, snippet.required, required=True)
        func = wrap_command(func, snippet.optional)
        if snippet.pagination:
            func = wrap_command(func, PAGINATION_OPTIONS)
        return func

    return wrapper


def run_graphql(context: StackletContext, name=None, variables=None, snippet=None, raw=False):
    executor = StackletGraphqlExecutor(context)

    if variables is None:
        variables = {}

    registry_snippet = StackletGraphqlExecutor.registry.get(name)

    for k, v in variables.items():
        transformer = registry_snippet.variable_transformers.get(k)
        if not transformer:
            continue
        variables[k] = transformer(v)

    if name and registry_snippet:
        snippet = registry_snippet
    elif name and registry_snippet is None:
        raise Exception("No snippet found, got name:%s snippet:%s" % (name, registry_snippet))

    res = executor.run(snippet=snippet, variables=variables)
    if raw:
        return res
    fmt = context.formatter()
    return fmt(res)
