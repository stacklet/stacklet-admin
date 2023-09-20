# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import yaml
from unittest.mock import patch

from utils import BaseCliTest, get_executor_adapter


class GraphqlTest(BaseCliTest):
    def test_executor_run(self):
        executor, adapter = get_executor_adapter()
        self.assertEqual(executor.token, "foo")
        self.assertEqual(executor.api, "mock://stacklet.acme.org/api")
        self.assertEqual(executor.session.headers["authorization"], "foo")

        adapter.register_uri(
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

        self.assertEqual(
            results,
            {
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

    def test_graphql_executor_via_cli(self):
        executor, adapter = get_executor_adapter()

        snippet = '{ platform { dashboardDefinition(name:"cis-v140") } }'
        adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json={"data": {"platform": {"version": "1.2.3+git.abcdef0"}}},
        )

        with patch(
            "stacklet.client.platform.executor.requests.Session", autospec=True
        ) as patched:
            with patch(
                "stacklet.client.platform.executor.get_token", return_value="foo"
            ):
                patched.return_value = executor.session
                res = self.runner.invoke(
                    self.cli,
                    [
                        "graphql",
                        "--api=mock://stacklet.acme.org/api",
                        "--cognito-region=us-east-1",
                        "--cognito-user-pool-id=foo",
                        "--cognito-client-id=bar",
                        "run",
                        f"--snippet={snippet}",
                    ],
                )
                body = json.loads(adapter.last_request.body.decode("utf-8"))
                assert body == {"query": snippet}

                assert res.exit_code == 0
                assert yaml.safe_load(res.output) == {
                    "data": {"platform": {"version": "1.2.3+git.abcdef0"}}
                }
