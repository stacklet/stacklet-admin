# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

from stacklet.client.platform.client import platform_client


@patch("stacklet.client.platform.client.StackletContext")
def test_client_loaded_commands(_, sample_config_file):
    with patch("stacklet.client.platform.client.DEFAULT_CONFIG_FILE", sample_config_file):
        client = platform_client()
    for attr in ("list_bindings", "list_accounts", "list_repository", "list_policies"):
        assert hasattr(client, attr)
