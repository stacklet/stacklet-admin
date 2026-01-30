# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from functools import cached_property
from pathlib import Path

from .config import DEFAULT_CONFIG_FILE, DEFAULT_OUTPUT_FORMAT, StackletConfig, StackletCredentials
from .exceptions import MissingToken
from .formatter import FORMATTERS, Formatter
from .graphql import GraphQLExecutor


class StackletContext:
    """CLI Execution Context."""

    formatter: Formatter
    credentials: StackletCredentials

    def __init__(
        self,
        config_file: Path = DEFAULT_CONFIG_FILE,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
    ):
        self.config_file = config_file
        self.formatter = FORMATTERS.get(output_format)
        self.credentials = StackletCredentials()

    @cached_property
    def config(self) -> StackletConfig:
        return StackletConfig.from_file(self.config_file)

    @cached_property
    def executor(self) -> GraphQLExecutor:
        token = self.credentials.api_token()
        if not token:
            raise MissingToken()

        return GraphQLExecutor(self.config.api, token)
