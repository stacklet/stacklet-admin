# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json

import pytest

from stacklet.client.platform.client import platform_client
from stacklet.client.platform.graphql import GRAPHQL_SNIPPETS


class TestPlatformClient:
    @pytest.fixture(autouse=True)
    def _setup(self, requests_adapter, default_config_file, sample_config, api_token_in_file):
        # confiuration is looked up in the default path
        default_config_file.write_text(json.dumps(sample_config))

        self.requests_adapter = requests_adapter

    def api_payloads(self, *payloads):
        self.requests_adapter.register_uri(
            "POST", "mock://stacklet.acme.org/api", [{"json": payload} for payload in payloads]
        )

    def api_requests(self):
        return [
            json.loads(response.body.decode()) for response in self.requests_adapter.request_history
        ]

    def test_snippets_as_methods(self):
        client = platform_client()

        for name in GRAPHQL_SNIPPETS:
            method_name = name.replace("-", "_")
            method = getattr(client, method_name)
            assert method is not None, f"client is missing method {method}"
            assert callable(method)

    def test_method_calls_snippet(self):
        payload = {
            "data": {
                "policy": {
                    "id": "1",
                    "name": "some-policy",
                }
            }
        }
        self.api_payloads(payload)

        client = platform_client()
        result = client.show_policy(name="some-policy")

        assert result == payload

        [request] = self.api_requests()
        assert "policy" in request["query"]
        assert request["variables"] == {"name": "some-policy"}

    def test_method_without_expr_filter(self):
        payload = {
            "data": {
                "accounts": {
                    "edges": [
                        {"node": {"id": "1", "name": "Account 1"}},
                        {"node": {"id": "2", "name": "Account 2"}},
                    ]
                }
            }
        }
        self.api_payloads(payload)

        client = platform_client()
        result = client.list_accounts()

        assert result == payload

    def test_method_with_expr_filter(self):
        payload = {
            "data": {
                "accounts": {
                    "edges": [
                        {"node": {"id": "1", "name": "Account 1"}},
                        {"node": {"id": "2", "name": "Account 2"}},
                    ]
                }
            }
        }
        self.api_payloads(payload)

        client = platform_client(expr=True)
        result = client.list_accounts()

        assert result == [
            {"id": "1", "name": "Account 1"},
            {"id": "2", "name": "Account 2"},
        ]

    def test_method_with_pagination(self):
        page1 = {
            "data": {
                "accounts": {
                    "edges": [{"node": {"id": "1", "name": "Account 1"}}],
                    "pageInfo": {
                        "hasNextPage": True,
                        "hasPreviousPage": False,
                        "startCursor": "cursor1",
                        "endCursor": "cursor2",
                        "total": 2,
                    },
                }
            }
        }
        page2 = {
            "data": {
                "accounts": {
                    "edges": [{"node": {"id": "2", "name": "Account 2"}}],
                    "pageInfo": {
                        "hasNextPage": False,
                        "hasPreviousPage": True,
                        "startCursor": "cursor2",
                        "endCursor": "cursor3",
                        "total": 2,
                    },
                }
            }
        }

        self.api_payloads(page1, page2)

        client = platform_client(pager=True)
        result = client.list_accounts()

        assert result == [page1, page2]
        assert len(self.api_requests()) == 2

        # Verify second request has the after cursor from first page
        [_, request2] = self.api_requests()
        assert request2["variables"]["after"] == "cursor2"

    def test_method_with_pagination_and_expr(self):
        page1 = {
            "data": {
                "accounts": {
                    "edges": [
                        {"node": {"id": "1", "name": "Account 1"}},
                        {"node": {"id": "2", "name": "Account 2"}},
                    ],
                    "pageInfo": {
                        "hasNextPage": True,
                        "hasPreviousPage": False,
                        "startCursor": "cursor1",
                        "endCursor": "cursor2",
                        "total": 4,
                    },
                }
            }
        }
        page2 = {
            "data": {
                "accounts": {
                    "edges": [
                        {"node": {"id": "3", "name": "Account 3"}},
                        {"node": {"id": "4", "name": "Account 4"}},
                    ],
                    "pageInfo": {
                        "hasNextPage": False,
                        "hasPreviousPage": True,
                        "startCursor": "cursor2",
                        "endCursor": "cursor3",
                        "total": 4,
                    },
                }
            }
        }

        self.api_payloads(page1, page2)

        client = platform_client(pager=True, expr=True)
        result = client.list_accounts()

        assert result == [
            {"id": "1", "name": "Account 1"},
            {"id": "2", "name": "Account 2"},
            {"id": "3", "name": "Account 3"},
            {"id": "4", "name": "Account 4"},
        ]

    def test_method_with_expr_not_paginated(self):
        payload = {"data": {"addAccount": {"account": {"id": "1", "name": "New Account"}}}}
        self.api_payloads(payload)

        client = platform_client(expr=True)
        result = client.add_account(provider="aws", key="123456789012")

        assert result == {"id": "1", "name": "New Account"}
