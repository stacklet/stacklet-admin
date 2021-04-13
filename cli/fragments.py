import logging
from string import Template


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
