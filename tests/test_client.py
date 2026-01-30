# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json

import pytest

from stacklet.client.platform.client import platform_client
from stacklet.client.platform.graphql import GRAPHQL_SNIPPETS


class TestPlatformClient:
    @pytest.fixture(autouse=True)
    def _setup(self, default_config_file, sample_config, api_token_in_file):
        # confiuration is looked up in the default path
        default_config_file.write_text(json.dumps(sample_config))

    def test_snippets_as_methods(self):
        client = platform_client()

        for name in GRAPHQL_SNIPPETS:
            method_name = name.replace("-", "_")
            method = getattr(client, method_name)
            assert method is not None, f"client is missing method {method}"
            assert callable(method)

    def test_method_calls_snippet(self, requests_adapter):
        payload = {"data": {"sample": "result"}}
        requests_adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json=payload,
        )

        client = platform_client()
        assert client.list_accounts() == payload

        # check the actual request payload
        request_body = json.loads(requests_adapter.last_request.body.decode())
        assert "accounts" in request_body["query"]
        assert request_body["variables"] == {
            "first": 20,
            "last": 0,
            "before": "",
            "after": "",
        }
