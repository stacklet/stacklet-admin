import json
import logging
from string import Template

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


class StackletFragment:
    def __init__(self, variables=None):
        # usage of string.Template is key here to prevent the need to use
        # double braces on every curly brace ({}) as graphql is full of those
        # in its syntax
        self.log = logging.getLogger("StackletFragment")
        self.log.info("Preparing Fragment:%s" % self.name)
        if variables:
            self.fragment = Template(self.fragment).substitute(**variables)
        self.log.info("Created Fragment: %s" % self.fragment)


@StackletFragmentExecutor.registry.register("list-accounts")
class QueryAccountFragment(StackletFragment):
    name = "list-accounts"
    fragment = """
        query {
            accounts {
                edges {
                    node {
                        name
                        id
                        key
                        provider
                        path
                        securityContext
                    }
                }
            }
        }
    """
    required = {}


@StackletFragmentExecutor.registry.register("add-account")
class AddAccountFragment(StackletFragment):
    name = "add-account"
    fragment = """
    mutation {
      addAccount(input:{
        provider: AWS,
        key:"$key",
        name:"$name",
        path:"$path",
        email:"$email",
        securityContext:"$security_context"
      }){
        status
      }
    }
    """
    required = {
        "key": "Account Key in Stacklet, e.g. Account ID in AWS",
        "name": "Account Name in Stacklet",
        "path": "Account Path",
        "email": "Account Email Address",
        "security_context": "Role for Custodian policy execution",
    }


@StackletFragmentExecutor.registry.register("add-repository")
class AddRepositoryFragment(StackletFragment):
    name = "add-repository"
    fragment = """
    mutation {
      addRepository(
        input: {
          url: "$url"
          name: "$name"
        }
      ) {
        status
      }
    }
    """
    required = {
        "url": "Policy Repository URL",
        "name": "Human Readable Policy Repository Name",
    }


@StackletFragmentExecutor.registry.register("process-repository")
class ProcessRepositoryFragment(StackletFragment):
    name = "process-repository"
    fragment = """
    mutation {
      processRepository(input:{url: "$url"}) {
        status
      }
    }
    """
    required = {"url": "Repository URL to process"}


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
