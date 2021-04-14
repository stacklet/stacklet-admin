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

    def __init__(self, name=None, snippet=None, variables=None):

        if name:
            self.name = name

        if snippet:
            self.snippet = snippet

        self.log = logging.getLogger("StackletGraphqlSnippet")

        # usage of string.Template is key here to prevent the need to use
        # double braces on every curly brace ({}) as graphql is full of those
        # in its syntax
        self.log.debug("Preparing Snippet:%s" % self.name)
        if variables:
            self.snippet = Template(self.snippet).substitute(**variables)

        self.log.debug("Created Snippet: %s" % self.snippet)
