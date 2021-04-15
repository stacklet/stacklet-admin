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


def wrap_command(func, options, required=False, prompt=False):
    for name, details in options.items():
        if isinstance(details, str):
            click.option(
                f'--{name.replace("_", "-")}',
                required=required,
                help=details,
                prompt=prompt,
            )(func)
        elif isinstance(details, dict):
            click.option(
                f'--{name.replace("_", "-")}',
                required=required,
                prompt=prompt,
                **details,
            )(func)
        else:
            raise Exception(
                "Options should be of type str or dict, got %s" % type(details)
            )
    return func


def snippet_options(*args, **kwargs):
    snippet_name = args[0]
    snippet = StackletGraphqlExecutor.registry.get(snippet_name)

    def wrapper(func):
        if not snippet:
            return func
        func = wrap_command(func, snippet.required, required=True, prompt=True)
        func = wrap_command(func, snippet.optional)
        return func

    return wrapper


def _run_graphql(ctx, name=None, variables=None, snippet=None):
    with StackletContext(ctx.obj["config"], ctx.obj["raw_config"]) as context:
        token = get_token()
        executor = StackletGraphqlExecutor(context, token)

        if variables is None:
            variables = {}
        variables.update(ctx.obj["page_variables"])

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
