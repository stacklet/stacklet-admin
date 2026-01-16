# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import requests_mock
import yaml

from .utils import BaseCliTest


class GraphqlTest(BaseCliTest):
    def test_executor_run(self):
        self.assertEqual(self.executor.api, "mock://stacklet.acme.org/api")
        self.assertEqual(self.executor.session.headers["authorization"], "mock-token")

        self.adapter.register_uri(
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

        snippet = self.executor.registry.get("list-accounts")

        results = self.executor.run(
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
        snippet = '{ platform { dashboardDefinition(name:"cis-v140") } }'

        payload = {"data": {"platform": {"version": "1.2.3+git.abcdef0"}}}
        self.adapter.post(requests_mock.ANY, json=payload)
        res = self.runner.invoke(
            self.cli,
            [
                "--api=mock://stacklet.acme.org/api",
                "--cognito-region=us-east-1",
                "--cognito-user-pool-id=foo",
                "--cognito-client-id=bar",
                "graphql",
                "run",
                f"--snippet={snippet}",
            ],
        )
        assert res.exit_code == 0, f"CLI failed: {res.output}"
        assert yaml.safe_load(res.output) == payload
