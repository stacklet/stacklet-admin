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

    def build(self):
        split_snippet = self.snippet.split("\n")

        # remove empty options so we can remove any optional values in the mutation/queries
        for k, v in self.input_variables.items():
            if v is None and k in snippet.optional.keys():
                split_snippet = [
                    line
                    for line in split_snippet
                    if f"${k.replace('-', '_')}" not in line
                ]

        build_snippet = "\n".join(build_snippet)
        d = {"query": self.snippet}
        if self.input_varibles:
            d["variables"] = self.input_variables
        return d
