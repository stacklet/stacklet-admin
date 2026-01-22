# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests_mock
import yaml

from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.exceptions import MissingToken
from stacklet.client.platform.executor import StackletGraphqlExecutor


@pytest.fixture
def executor(mock_api_token, sample_config_file) -> StackletGraphqlExecutor:
    context = StackletContext(config_file=sample_config_file)
    return StackletGraphqlExecutor(context)


class TestGraphqlExecutor:
    def test_missing_token(self, sample_config_file):
        context = StackletContext(config_file=sample_config_file)
        with pytest.raises(MissingToken):
            StackletGraphqlExecutor(context)

    def test_executor_run(self, requests_adapter, executor):
        assert executor.api == "mock://stacklet.acme.org/api"
        assert executor.session.headers["authorization"] == "Bearer mock-token"

        requests_adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json={
                "data": {
                    "accounts": {
                        "edges": [
                            {
                                "node": {
                                    "email": "foo@bar.com",
                                    "id": "account:aws:123123123123",
                                    "key": "123123123123",
                                    "name": "test-account",
                                    "path": "/",
                                    "provider": "AWS",
                                }
                            }
                        ]
                    }
                }
            },
        )

        snippet = executor.registry.get("list-accounts")

        results = executor.run(
            snippet,
            variables={
                "provider": "AWS",
                "first": 1,
                "last": 1,
                "before": "",
                "after": "",
            },
        )

        assert results == {
            "data": {
                "accounts": {
                    "edges": [
                        {
                            "node": {
                                "email": "foo@bar.com",
                                "id": "account:aws:123123123123",
                                "key": "123123123123",
                                "name": "test-account",
                                "path": "/",
                                "provider": "AWS",
                            }
                        }
                    ]
                }
            }
        }

    def test_graphql_executor(
        self, requests_adapter, sample_config_file, invoke_cli, mock_api_token
    ):
        snippet = '{ platform { dashboardDefinition(name:"cis-v140") } }'

        payload = {"data": {"platform": {"version": "1.2.3+git.abcdef0"}}}
        requests_adapter.post(requests_mock.ANY, json=payload)
        res = invoke_cli(
            "graphql",
            "run",
            f"--snippet={snippet}",
        )
        assert res.exit_code == 0, f"CLI failed: {res.output}"
        assert yaml.safe_load(res.output) == payload
