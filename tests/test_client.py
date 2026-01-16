# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
from unittest.mock import patch

from stacklet.client.platform.client import platform_client


@patch("stacklet.client.platform.client.StackletContext")
def test_client_loaded_commands(_, config_file, sample_config):
    # write the config in the config file
    config_file.write_text(json.dumps(sample_config))

    with patch("stacklet.client.platform.client.DEFAULT_CONFIG_FILE", config_file):
        client = platform_client()
    assert hasattr(client, "list_bindings")
    assert hasattr(client, "list_accounts")
    assert hasattr(client, "list_repository")
    assert hasattr(client, "list_policies")
