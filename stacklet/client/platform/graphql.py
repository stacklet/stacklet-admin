# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import logging

import requests

from .config import JSONDict
from .exceptions import UnknownSnippet
from .registry import PluginRegistry
from .utils import USER_AGENT

GRAPHQL_SNIPPETS = PluginRegistry("StackletGraphqlSnippets")


class StackletGraphqlSnippet:
    """
    A reusable Graphql Snippet

    Define required variables with the required class attribute and optional
    variables with the optional class attribute. The value can either be a string
    or a dict. If the type is string, the value is passed in as the help text for
    the option. See example:

    .. code-block:: python

        class MySnippet(StackletGraphqlSnippet):

            name = 'my-snippet'
            snippet = '''
                query {
                    foo(
                        id: $id
                        bar: $bar
                        baz: $baz
                    ) {
                        id
                        description
                    }
                }
            '''

            required = {
                'id': {
                    'help': 'the id',
                    'type': click.Choice(['foo', 'bar'])
                },
                "bar": 'Another variable'
            }

            optional = {
                'baz': {
                    'help': 'An optional variable',
                    'default': 'blah'
                }
            }
    """

    def __init__(self):
        raise RuntimeError("instances don't do anything")

    name = None
    snippet = None
    required = {}
    optional = {}
    pagination = False
    input_variables = None
    parameter_types = {}
    variable_transformers = {}

    @classmethod
    def build(cls, variables: JSONDict | None):
        variables = cls._transform_variables(variables)

        if cls.snippet:
            split_snippet = list(filter(None, cls.snippet.split("\n")))
        else:
            split_snippet = []

        # remove empty options so we can remove any optional values in the mutation/queries
        for k in set(cls.optional).intersection(variables):
            if variables[k] is None or variables[k] == ():
                split_snippet = [
                    line for line in split_snippet if f"${k.replace('-', '_')}" not in line
                ]
        d = {}
        if variables:
            d["variables"] = {k: v for k, v in variables.items() if v is not None and v != ()}

        if var_names := d.get("variables", ()):
            qtype, bracked = split_snippet[0].strip().split(" ", 1)
            split_snippet[0] = "%s (%s) {" % (
                qtype,
                (
                    " ".join(
                        [
                            "$%s: %s," % (s, gql_type(variables[s], cls.parameter_types.get(s)))
                            for s in var_names
                        ]
                    )
                )[:-1],
            )
        d["query"] = "\n".join(split_snippet).replace('"', "")
        return d

    @classmethod
    def _transform_variables(cls, variables: JSONDict | None) -> JSONDict:
        if not variables:
            return {}

        for name, value in variables.items():
            if transformer := cls.variable_transformers.get(name):
                variables[name] = transformer(value)

        return variables


class AdHocSnippet(StackletGraphqlSnippet):
    """
    This exists to work around the mangling in StackletGraphQLSnippet which
    is inconvenient when trying to run simple queries that use e.g. quotes.

    We can worry about variable support when we need it.
    """

    @classmethod
    def build(cls, variables):
        if variables:
            raise NotImplementedError("AdHocSnippet needs variables support")
        return {"query": cls.snippet}


def gql_type(v, snippet_type=None):
    if snippet_type is not None:
        return snippet_type
    if isinstance(v, str):
        return "String!"
    elif isinstance(v, bool):
        return "Boolean!"
    elif isinstance(v, int):
        return "Int!"
    elif isinstance(v, list) or isinstance(v, tuple):
        return "[%s]" % (gql_type(v[0]))
    else:
        raise ValueError("unsupported %s" % (type(v)))


class StackletGraphqlExecutor:
    """Execute Graphql queries against the API."""

    def __init__(self, api: str, token: str):
        self.api = api
        self.token = token
        self.log = logging.getLogger("StackletGraphqlExecutor")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "User-Agent": USER_AGENT,
            }
        )

    def run(self, name: str, variables: JSONDict | None = None) -> JSONDict:
        """Run a named graphql snippet."""
        snippet = GRAPHQL_SNIPPETS.get(name)
        if not snippet:
            raise UnknownSnippet(name)

        return self._run_snippet(snippet, variables=variables)

    def run_query(self, query: str) -> JSONDict:
        """Run a literal GraphQL query string."""
        snippet = type("AdHocSnippet", (AdHocSnippet,), {"snippet": query})
        return self._run_snippet(snippet)

    def _run_snippet(
        self, snippet: type[StackletGraphqlSnippet], variables: JSONDict | None = None
    ) -> JSONDict:
        request = snippet.build(variables)
        self.log.debug("Request: %s" % json.dumps(request, indent=2))
        res = self.session.post(self.api, json=request)
        self.log.debug("Response: %s" % json.dumps(res.json(), indent=2))
        return res.json()
