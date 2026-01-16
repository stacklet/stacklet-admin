# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
from textwrap import dedent

from .utils import BaseCliTest, JSONDict


class RepositoryTest(BaseCliTest):
    def test_add_repository(self):
        res, body = self.run_query(
            "repository",
            [
                "add",
                "--url=mock://git.acme.org/stacklet/policies.git",
                "--name=test-policies",
            ],
            response=JSONDict(
                data={
                    "addRepository": {
                        "url": "mock://git.acme.org/stacklet/policies.git",
                        "name": "test-policies",
                    }
                }
            ),
        )
        assert res.output == dedent(
            """\
            data:
              addRepository:
                name: test-policies
                url: mock://git.acme.org/stacklet/policies.git

            """
        )

        assert (
            body["query"].strip()
            == """mutation ($url: String!, $name: String!) {
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
    }"""
        )

    def test_add_repository_deep(self):
        res, body = self.run_query(
            "repository",
            [
                "add",
                "--url=mock://git.acme.org/stacklet/policies.git",
                "--name=test-policies",
                "--deep-import=true",
            ],
            response=JSONDict(
                data={
                    "addRepository": {
                        "url": "mock://git.acme.org/stacklet/policies.git",
                        "name": "test-policies",
                    }
                }
            ),
        )
        assert res.output == dedent(
            """\
            data:
              addRepository:
                name: test-policies
                url: mock://git.acme.org/stacklet/policies.git

            """
        )

        assert (
            body["query"].strip()
            == """mutation ($url: String!, $name: String!, $deep_import: Boolean!) {
      addRepository(
        input: {
          url: $url
          name: $name
          deepImport: $deep_import
        }
      ) {
        repository {
            url
            name
        }
      }
    }"""
        )
        # Check the conversion of string to bool.
        assert body["variables"] == {
            "deep_import": True,
            "name": "test-policies",
            "url": "mock://git.acme.org/stacklet/policies.git",
        }

    def test_process_repository(self):
        self.adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json={"data": {"processRepository": "34c10c3e-d841-4e63-9d51-01b92f36c502"}},
        )
        res = self.runner.invoke(
            self.cli,
            [
                "--api=mock://stacklet.acme.org/api",
                "--cognito-region=us-east-1",
                "--cognito-user-pool-id=foo",
                "--cognito-client-id=bar",
                "repository",
                "process",
                "--url=mock://git.acme.org/stacklet/policies.git",
            ],
        )
        self.assertEqual(res.exit_code, 0)
        self.assertEqual(
            res.output,
            "data:\n  processRepository: 34c10c3e-d841-4e63-9d51-01b92f36c502\n\n",
        )
        body = json.loads(self.adapter.last_request.body.decode("utf-8"))
        self.assertEqual(
            body["query"].strip(),
            """mutation ($url: String!) {
      processRepository(input:{url: $url})
    }""",
        )
