# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json

from stacklet.client.platform.client import platform_client


def test_client_loaded_commands(default_config_file, sample_config, api_token_in_file):
    default_config_file.write_text(json.dumps(sample_config))
    client = platform_client()
    for attr in ("list_bindings", "list_accounts", "list_repository", "list_policies"):
        assert hasattr(client, attr)
