# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from stacklet.client.platform.config import StackletConfig


class StackletContext:
    """
    CLI Execution Context
    """

    DEFAULT_CONFIG_DIR = Path("~/.stacklet").expanduser()
    DEFAULT_CONFIG = DEFAULT_CONFIG_DIR / "config.json"
    DEFAULT_CREDENTIALS = DEFAULT_CONFIG_DIR / "credentials"
    DEFAULT_ID = DEFAULT_CONFIG_DIR / "id"

    def __init__(self, config=None, raw_config=None):
        if len(raw_config.values()) != 0:
            self.config = StackletConfig(**raw_config)
        elif config:
            self.config = StackletConfig.from_file(config)
        else:
            self.config = StackletConfig.from_file(self.DEFAULT_CONFIG)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return

    def can_sso_login(self):
        return all(
            [
                self.config.auth_url,
                self.config.cognito_client_id,
            ]
        )
