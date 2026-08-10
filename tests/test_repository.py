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
                    "addRepositoryConfig": {
                        "repositoryConfig": {
                            "uuid": "34c10c3e-d841-4e63-9d51-01b92f36c502",
                            "url": "mock://git.acme.org/stacklet/policies.git",
                            "name": "test-policies",
                        },
                        "problems": [],
                    }
                }
            },
        )
        assert res.output == dedent(
            """\
            data:
              addRepositoryConfig:
                problems: []
                repositoryConfig:
                  name: test-policies
                  url: mock://git.acme.org/stacklet/policies.git
                  uuid: 34c10c3e-d841-4e63-9d51-01b92f36c502

            """
        )

        assert_query(
            body,
            """
            mutation ($url: String!, $name: String!) {
              addRepositoryConfig(
                input: {
                  url: $url
                  name: $name
                  auth: {
                  }
                }
              ) {
                repositoryConfig {
                    uuid
                    url
                    name
                }
                problems {
                    message
                }
              }
            }
            """,
        )

    def test_add_repository_with_auth(self, run_query):
        res, body = run_query(
            "repository",
            [
                "add",
                "--url=mock://git.acme.org/stacklet/policies.git",
                "--name=test-policies",
                "--auth-user=someuser",
                "--auth-token=sometoken",
            ],
            response={
                "data": {
                    "addRepositoryConfig": {
                        "repositoryConfig": {
                            "uuid": "34c10c3e-d841-4e63-9d51-01b92f36c502",
                            "url": "mock://git.acme.org/stacklet/policies.git",
                            "name": "test-policies",
                        },
                        "problems": [],
                    }
                }
            },
        )
        assert res.exit_code == 0

        assert_query(
            body,
            """
            mutation ($url: String!, $name: String!, $auth_user: String!, $auth_token: String!) {
              addRepositoryConfig(
                input: {
                  url: $url
                  name: $name
                  auth: {
                    authUser: $auth_user
                    authToken: $auth_token
                  }
                }
              ) {
                repositoryConfig {
                    uuid
                    url
                    name
                }
                problems {
                    message
                }
              }
            }
            """,
        )
        assert body["variables"] == {
            "url": "mock://git.acme.org/stacklet/policies.git",
            "name": "test-policies",
            "auth_user": "someuser",
            "auth_token": "sometoken",
        }

    def test_process_repository(self, run_query):
        res, body = run_query(
            "repository",
            [
                "process",
                "--uuid=34c10c3e-d841-4e63-9d51-01b92f36c502",
            ],
            response={"data": {"triggerRepositoryScan": {"problems": []}}},
        )
        assert res.output == "data:\n  triggerRepositoryScan:\n    problems: []\n\n"
        assert_query(
            body,
            """
            mutation ($uuid: String!) {
              triggerRepositoryScan(input:{uuid: $uuid}) {
                problems {
                    message
                }
              }
            }
            """,
        )
