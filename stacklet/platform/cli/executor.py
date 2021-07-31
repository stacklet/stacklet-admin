import json
import logging

import requests
from c7n.registry import PluginRegistry
from stacklet.platform.cli.context import StackletContext
from stacklet.platform.cli.formatter import Formatter
from stacklet.platform.cli.graphql import StackletGraphqlSnippet
from stacklet.platform.cli.utils import _PAGINATION_OPTIONS, get_token, wrap_command


class StackletGraphqlExecutor:
    """
    Execute Graphql against the API
    """

    registry = PluginRegistry("StackletGraphqlSnippets")

    def __init__(self, context, token):
        self.context = context
        self.api = self.context.config.api
        self.token = token
        self.log = logging.getLogger("StackletGraphqlExecutor")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": self.token,
            }
        )

    def run(self, snippet, variables=None):
        if variables is None:
            variables = {}

        split_snippet = snippet.snippet.split("\n")

        for k, v in variables.items():
            if not v and k in snippet.optional.keys():
                split_snippet = [
                    line
                    for line in split_snippet
                    if f"${k.replace('-', '_')}" not in line
                ]
        snippet.snippet = "\n".join(split_snippet)

        payload = snippet
        if not isinstance(snippet, StackletGraphqlSnippet):
            payload = snippet(variables=variables)

        res = self.session.post(self.api, json={"query": payload.snippet})
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
            func = wrap_command(func, _PAGINATION_OPTIONS)
        return func

    return wrapper


def _run_graphql(ctx, name=None, variables=None, snippet=None):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        token = get_token()
        executor = StackletGraphqlExecutor(context, token)

        if variables is None:
            variables = {}

        registry_snippet = StackletGraphqlExecutor.registry.get(name)
        if name and registry_snippet:
            snippet = registry_snippet
        elif name and registry_snippet is None:
            raise Exception(
                "No snippet found, got name:%s snippet:%s" % (name, registry_snippet)
            )

        res = executor.run(snippet=snippet, variables=variables)

        fmt = Formatter.registry.get(ctx.obj["output"])()
        return fmt(res)
