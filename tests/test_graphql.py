# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests_mock

from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.graphql import StackletGraphqlExecutor, StackletGraphqlSnippet


@pytest.fixture
def executor(api_token_in_file, sample_config_file) -> StackletGraphqlExecutor:
    context = StackletContext(config_file=sample_config_file)
    return StackletGraphqlExecutor(context.config.api, context.credentials.api_token())


class TestGraphqlExecutor:
    def test_config(self, api_token_in_file, executor):
        assert executor.api == "mock://stacklet.acme.org/api"
        assert executor.session.headers["authorization"] == f"Bearer {api_token_in_file}"

    def test_executor_run(self, requests_adapter, executor):
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

        results = executor.run(
            "list-accounts",
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

    def test_executor_run_query(self, requests_adapter, executor):
        snippet = '{ platform { dashboardDefinition(name:"cis-v140") } }'

        payload = {"data": {"platform": {"version": "1.2.3+git.abcdef0"}}}
        requests_adapter.post(requests_mock.ANY, json=payload)
        assert executor.run_query(snippet) == payload


class TestStackletGraphqlSnippet:
    def test_build_expands_variables(self):
        class Snippet(StackletGraphqlSnippet):
            name = "sample"
            snippet = """
            query {
              sample(somevar: $somevar) {
                foo
                bar
              }
            }
            """
            variable_transformers = {"somevar": lambda x: x.upper()}

        result = Snippet.build({"somevar": "test"})
        assert result == {
            "query": """query ($somevar: String!) {
              sample(somevar: $somevar) {
                foo
                bar
              }
            }
            """,
            "variables": {"somevar": "TEST"},
        }
