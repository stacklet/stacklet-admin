# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import patch

from stacklet.client.platform.client import platform_client


@patch("stacklet.client.platform.client.get_token")
@patch("stacklet.client.platform.client.StackletContext")
@patch("stacklet.client.platform.client.Path")
def test_client_loaded_commands(
    patched_path, patched_stacklet_context, patched_get_token
):
    client = platform_client()
    assert hasattr(client, "list_bindings")
    assert hasattr(client, "list_accounts")
    assert hasattr(client, "list_repository")
    assert hasattr(client, "list_policies")
