import json
from unittest.mock import patch

from utils import BaseCliTest, get_executor_adapter


class RepositoryTest(BaseCliTest):
    def test_add_repository(self):
        executor, adapter = get_executor_adapter()
        adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json={
                "data": {
                    "addRepository": {
                        "url": "mock://git.acme.org/stacklet/policies.git",
                        "name": "test-policies",
                    }
                }
            },
        )

        with patch(
            "stacklet.client.platform.executor.requests.Session", autospec=True
        ) as patched:
            with patch("stacklet.client.platform.executor.get_token", return_value="foo"):
                patched.return_value = executor.session
                res = self.runner.invoke(
                    self.cli,
                    [
                        "repository",
                        "--api=mock://stacklet.acme.org/api",
                        "--cognito-region=us-east-1",
                        "--cognito-user-pool-id=foo",
                        "--cognito-client-id=bar",
                        "add",
                        "--url=mock://git.acme.org/stacklet/policies.git",
                        "--name=test-policies",
                    ],
                )
                self.assertEqual(res.exit_code, 0)
                self.assertEqual(
                    res.output,
                    "data:\n  addRepository:\n    name: test-policies\n    url: mock://git.acme.org/stacklet/policies.git\n\n",  # noqa
                )
                body = json.loads(adapter.last_request.body.decode("utf-8"))
                self.assertEqual(
                    body["query"].strip(),
                    """mutation ($url: String!, $name: String!) {
      addRepository(
        input: {
          url: $url
          name: $name
        }
      ) {
        repository {
            url
            name
        }
      }
    }""",
                )

    def test_process_repository(self):
        executor, adapter = get_executor_adapter()
        adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json={"data": {"processRepository": {"status": True}}},
        )

        with patch(
            "stacklet.client.platform.executor.requests.Session", autospec=True
        ) as patched:
            with patch("stacklet.client.platform.executor.get_token", return_value="foo"):
                patched.return_value = executor.session
                res = self.runner.invoke(
                    self.cli,
                    [
                        "repository",
                        "--api=mock://stacklet.acme.org/api",
                        "--cognito-region=us-east-1",
                        "--cognito-user-pool-id=foo",
                        "--cognito-client-id=bar",
                        "process",
                        "--url=mock://git.acme.org/stacklet/policies.git",
                    ],
                )
                self.assertEqual(res.exit_code, 0)
                self.assertEqual(
                    res.output, "data:\n  processRepository:\n    status: true\n\n"
                )
                body = json.loads(adapter.last_request.body.decode("utf-8"))
                self.assertEqual(
                    body["query"].strip(),
                    """mutation ($url: String!) {
      processRepository(input:{url: $url}) {
        status
      }
    }""",
                )
