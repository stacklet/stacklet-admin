# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from functools import cached_property
from pathlib import Path

from .config import DEFAULT_CONFIG_FILE, DEFAULT_OUTPUT_FORMAT, StackletConfig, StackletCredentials
from .formatter import Formatter


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
        self.formatter = Formatter.registry.get(output_format)
        self.credentials = StackletCredentials()

    @cached_property
    def config(self) -> StackletConfig:
        return StackletConfig.from_file(self.config_file)
