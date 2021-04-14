import json
import logging

import click
import requests
from c7n.registry import PluginRegistry

from cli.context import StackletContext
from cli.formatter import Formatter
from cli.graphql import StackletGraphqlSnippet
from cli.utils import get_token


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
        self.session.headers.update({"authorization": self.token})

    def run(self, snippet, variables=None):
        if variables is None:
            variables = {}

        payload = snippet
        if not isinstance(snippet, StackletGraphqlSnippet):
            payload = snippet(variables=variables)

        res = self.session.post(self.api, json={"query": payload.snippet})
        res.raise_for_status()
        self.log.debug("Response: %s" % json.dumps(res.json(), indent=2))
        return res.json()


def snippet_options(*args, **kwargs):
    snippet_name = args[0]
    snippet = StackletGraphqlExecutor.registry.get(snippet_name)

    def wrapper(func):
        if not snippet:
            return func
        for option, help in snippet.required.items():
            click.option(
                f'--{option.replace("_", "-")}', required=True, help=help, prompt=True
            )(func)
        return func

    return wrapper


def _run_graphql(ctx, name=None, variables=None, snippet=None):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        token = get_token()
        executor = StackletGraphqlExecutor(context, token)

        registry_snippet = StackletGraphqlExecutor.registry.get(name)
        if name and registry_snippet:
            snippet = registry_snippet
        elif name and registry_snippet is None:
            raise Exception

        res = executor.run(snippet=snippet, variables=variables)

        fmt = Formatter.registry.get(ctx.obj["output"])()
        return fmt(res)
