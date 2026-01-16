# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any

from .config import DEFAULT_CONFIG_FILE, DEFAULT_OUTPUT_FORMAT, StackletConfig, StackletCredentials
from .formatter import Formatter


class StackletContext:
    """CLI Execution Context."""

    raw_config: dict[str, Any]
    formatter: Formatter
    config: StackletConfig
    credentials: StackletCredentials

    def __init__(
        self,
        raw_config: dict | None = None,
        config_file: str | None = None,
        output_format: str = DEFAULT_OUTPUT_FORMAT,
    ):
        self.formatter = Formatter.registry.get(output_format)
        self.credentials = StackletCredentials()

        if raw_config:
            self.config = StackletConfig(**raw_config)
        else:
            if not config_file:
                config_file = os.getenv("STACKLET_CONFIG", str(DEFAULT_CONFIG_FILE))
            self.config = StackletConfig.from_file(config_file)

    def can_sso_login(self):
        return all(
            [
                self.config.auth_url,
                self.config.cognito_client_id,
            ]
        )
