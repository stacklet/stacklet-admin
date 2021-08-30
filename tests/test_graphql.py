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

    def test_grpahql_executor_via_cli(self):
        snippet = """
{
    accounts (
    ){
        edges {
            node {
                id
            }
        }
    }
}
"""
        executor, adapter = get_executor_adapter()
        adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json={
                "data": {
                    "accounts": {
                        "edges": [
                            {
                                "node": {
                                    "id": "account:aws:123123123123",
                                }
                            }
                        ]
                    }
                }
            },
        )

        with patch(
            "stacklet.platform.cli.executor.requests.Session", autospec=True
        ) as patched:
            with patch("stacklet.platform.cli.executor.get_token", return_value="foo"):
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
                print(res.output)
                self.assertEqual(res.exit_code, 0)

                self.assertEqual(
                    res.output,
                    "data:\n  accounts:\n    edges:\n    - node:\n        id: account:aws:123123123123\n\n",  # noqa
                )
