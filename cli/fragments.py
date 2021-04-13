import logging
from string import Template


class StackletFragment:
    def __init__(self, name=None, fragment=None, variables=None):
        # usage of string.Template is key here to prevent the need to use
        # double braces on every curly brace ({}) as graphql is full of those
        # in its syntax

        if name:
            self.name = name

        if fragment:
            self.fragment = fragment

        self.log = logging.getLogger("StackletFragment")
        self.log.info("Preparing Fragment:%s" % self.name)
        if variables:
            self.fragment = Template(self.fragment).substitute(**variables)
        self.log.info("Created Fragment: %s" % self.fragment)
