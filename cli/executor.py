import json
import logging

import click
import requests
from c7n.registry import PluginRegistry

from cli.context import StackletContext
from cli.formatter import Formatter
from cli.utils import get_token


class StackletFragmentExecutor:
    """
    Execute Graphql Fragments against the API
    """

    registry = PluginRegistry("StackletFragments")

    def __init__(self, context, token):
        self.context = context
        self.api = self.context.config.api
        self.token = token
        self.log = logging.getLogger("StackletFragmentExecutor")

        self.session = requests.Session()
        self.session.headers.update({"authorization": self.token})

    def run(self, fragment, variables=None):
        if variables is None:
            variables = {}
        res = self.session.post(self.api, json={"query": fragment(variables).fragment})
        res.raise_for_status()
        self.log.info("Response: %s" % json.dumps(res.json(), indent=2))
        return res.json()


def fragment_options(*args, **kwargs):
    fragment_name = args[0]
    fragment = StackletFragmentExecutor.registry.get(fragment_name)

    def wrapper(func):
        if not fragment:
            return func
        for option, help in fragment.required.items():
            click.option(
                f'--{option.replace("_", "-")}', required=True, help=help, prompt=True
            )(func)
        return func

    return wrapper


def _run_fragment(ctx, name, variables=None):
    with StackletContext(ctx.obj["config"]) as context:
        token = get_token()
        executor = StackletFragmentExecutor(context, token)
        res = executor.run(
            StackletFragmentExecutor.registry.get(name), variables=variables
        )
        fmt = Formatter.registry.get(ctx.obj["output"])()
        return fmt(res)
