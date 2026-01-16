# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from textwrap import dedent

from .asserts import assert_query


class TestRepository:
    def test_add_repository(self, run_query):
        res, body = run_query(
            "repository",
            [
                "add",
                "--url=mock://git.acme.org/stacklet/policies.git",
                "--name=test-policies",
            ],
            response={
                "data": {
                    "addRepository": {
                        "url": "mock://git.acme.org/stacklet/policies.git",
                        "name": "test-policies",
                    }
                }
            },
        )
        assert res.output == dedent(
            """\
            data:
              addRepository:
                name: test-policies
                url: mock://git.acme.org/stacklet/policies.git

            """
        )

        assert_query(
            body,
            """
            mutation ($url: String!, $name: String!) {
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
            }
            """,
        )

    def test_add_repository_deep(self, run_query):
        res, body = run_query(
            "repository",
            [
                "add",
                "--url=mock://git.acme.org/stacklet/policies.git",
                "--name=test-policies",
                "--deep-import=true",
            ],
            response={
                "data": {
                    "addRepository": {
                        "url": "mock://git.acme.org/stacklet/policies.git",
                        "name": "test-policies",
                    }
                }
            },
        )
        assert res.output == dedent(
            """\
            data:
              addRepository:
                name: test-policies
                url: mock://git.acme.org/stacklet/policies.git

            """
        )

        assert_query(
            body,
            """
            mutation ($url: String!, $name: String!, $deep_import: Boolean!) {
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
            }
            """,
        )
        # Check the conversion of string to bool.
        assert body["variables"] == {
            "deep_import": True,
            "name": "test-policies",
            "url": "mock://git.acme.org/stacklet/policies.git",
        }

    def test_process_repository(self, run_query):
        res, body = run_query(
            "repository",
            [
                "process",
                "--url=mock://git.acme.org/stacklet/policies.git",
            ],
            response={"data": {"processRepository": "34c10c3e-d841-4e63-9d51-01b92f36c502"}},
        )
        assert res.output == "data:\n  processRepository: 34c10c3e-d841-4e63-9d51-01b92f36c502\n\n"
        assert_query(
            body,
            """
            mutation ($url: String!) {
              processRepository(input:{url: $url})
            }
            """,
        )
