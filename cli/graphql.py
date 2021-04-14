import logging
from string import Template


class StackletGraphqlSnippet:

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
