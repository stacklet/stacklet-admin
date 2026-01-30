# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from ..config import JSONDict


class GraphQLSnippet:
    """
    A reusable GraphQL Snippet

    Define required variables with the required class attribute and optional
    variables with the optional class attribute. The value can either be a string
    or a dict. If the type is string, the value is passed in as the help text for
    the option. See example:

    .. code-block:: python

        class MySnippet(GraphQLSnippet):

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

    name: str
    snippet: str
    required = {}
    optional = {}
    pagination = False
    input_variables = None
    parameter_types = {}
    variable_transformers = {}

    def __init__(self):
        raise RuntimeError("instances don't do anything")

    @classmethod
    def build(cls, variables: JSONDict | None):
        if variables is None:
            variables = {}

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
            qtype, _ = split_snippet[0].strip().split(" ", 1)
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
    def transform_variables(cls, variables: JSONDict | None) -> JSONDict:
        variables = variables.copy() if variables else {}

        for name, value in variables.items():
            if transformer := cls.variable_transformers.get(name):
                variables[name] = transformer(value)

        return variables


class AdHocSnippet(GraphQLSnippet):
    """
    This exists to work around the mangling in GraphQLSnippet which
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
