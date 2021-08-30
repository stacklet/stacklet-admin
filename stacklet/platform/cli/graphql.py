import logging
from string import Template


class StackletGraphqlSnippet:
    """
    A resusable Graphql Snippet

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

    name = None
    snippet = None
    required = {}
    optional = {}
    pagination = False
    input_variables = None

    def __init__(self, name=None, snippet=None, variables=None):

        if name:
            self.name = name

        if snippet:
            self.snippet = snippet

        if variables is None:
            variables = {}

        self.log = logging.getLogger("StackletGraphqlSnippet")

        # usage of string.Template is key here to prevent the need to use
        # double braces on every curly brace ({}) as graphql is full of those
        # in its syntax
        self.log.debug("Preparing Snippet:%s" % self.name)
        self.snippet = snippet
        self.input_variables = variables
        self.log.debug("Created Snippet: %s" % self.snippet)

    @classmethod
    def build(cls, variables):
        split_snippet = cls.snippet.split("\n")

        # remove empty options so we can remove any optional values in the mutation/queries
        for k in set(cls.optional).intersection(variables):
            if variables[k] is None:
                split_snippet = [
                    line
                    for line in split_snippet
                    if f"${k.replace('-', '_')}" not in line
                ]
        d = {"query": "\n".join(split_snippet)}
        if variables:
            d["variables"] = {k: v for k, v in variables.items() if v is not None}
        return d
