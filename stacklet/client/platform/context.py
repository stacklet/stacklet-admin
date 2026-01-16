# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import os

from .config import DEFAULT_CONFIG_FILE, StackletConfig


class StackletContext:
    """CLI Execution Context."""

    def __init__(self, raw_config: dict | None = None, config_file: str | None = None):
        self.raw_config = raw_config
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
