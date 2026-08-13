# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from textwrap import dedent

from .asserts import assert_query, assert_query_contains

REPO_UUID = "34c10c3e-d841-4e63-9d51-01b92f36c502"
COLLECTION_UUID = "9f1d9a9c-3a1e-4d0a-9c3b-2b0f5f9c1a77"
REPO_URL = "mock://git.acme.org/stacklet/policies.git"

ADD_CONFIG_RESPONSE = {
    "data": {
        "addRepositoryConfig": {
            "repositoryConfig": {"uuid": REPO_UUID, "url": REPO_URL, "name": "test-policies"},
            "problems": [],
        }
    }
}
ADD_COLLECTION_RESPONSE = {
    "data": {
        "addPolicyCollection": {
            "collection": {"uuid": COLLECTION_UUID, "name": "test-policies", "isDynamic": True}
        }
    }
}


class TestRepositoryRegister:
    """`repository register` drives addRepositoryConfig then addPolicyCollection."""

    def test_register(self, run_queries):
        res, bodies = run_queries(
            "repository",
            ["register", f"--url={REPO_URL}", "--name=test-policies", "--provider=AWS"],
            [ADD_CONFIG_RESPONSE, ADD_COLLECTION_RESPONSE],
        )
        assert res.exit_code == 0, res.output
        assert len(bodies) == 2

        config, collection = bodies
        assert config["variables"] == {"url": REPO_URL, "name": "test-policies"}
        assert_query_contains(config, "addRepositoryConfig")

        # The collection is wired to the new config, defaults its name to the
        # repository's, and is auto-updating because a dynamic collection must be.
        assert collection["variables"] == {
            "name": "test-policies",
            "provider": "AWS",
            "repository_uuid": REPO_UUID,
            "auto_update": True,
        }

        # Both halves are reported: the config alone would scan nothing.
        assert "repositoryConfig:" in res.output
        assert "policyCollection:" in res.output
        assert COLLECTION_UUID in res.output

    def test_register_deep_import(self, run_queries):
        "--deep-import is shorthand for the TAIL start revision."
        res, bodies = run_queries(
            "repository",
            [
                "register",
                f"--url={REPO_URL}",
                "--name=test-policies",
                "--provider=AWS",
                "--collection-name=history",
                "--deep-import",
                "--branch-name=main",
            ],
            [ADD_CONFIG_RESPONSE, ADD_COLLECTION_RESPONSE],
        )
        assert res.exit_code == 0, res.output
        assert bodies[1]["variables"] == {
            "name": "history",
            "provider": "AWS",
            "repository_uuid": REPO_UUID,
            "auto_update": True,
            "branch_name": "main",
            "start_rev_spec": "TAIL",
        }

    def test_register_deep_import_conflicts_with_start_rev_spec(self, run_queries):
        res, bodies = run_queries(
            "repository",
            [
                "register",
                f"--url={REPO_URL}",
                "--name=test-policies",
                "--provider=AWS",
                "--deep-import",
                "--start-rev-spec=abc123",
            ],
            [],
        )
        assert res.exit_code != 0
        assert "--deep-import and --start-rev-spec are exclusive" in res.output
        # Rejected before the repository was created.
        assert bodies == []

    def test_register_reports_repository_problems(self, run_queries):
        res, bodies = run_queries(
            "repository",
            ["register", f"--url={REPO_URL}", "--name=test-policies", "--provider=AWS"],
            [
                {
                    "data": {
                        "addRepositoryConfig": {"problems": [{"message": "url is not reachable"}]}
                    }
                }
            ],
        )
        assert res.exit_code != 0
        assert "could not add repository: url is not reachable" in res.output
        # No collection attempted for a repository that wasn't created.
        assert len(bodies) == 1

    def test_register_reports_orphaned_repository(self, run_queries):
        "If the collection fails the config still exists, and won't scan anything."
        res, bodies = run_queries(
            "repository",
            ["register", f"--url={REPO_URL}", "--name=test-policies", "--provider=AWS"],
            [ADD_CONFIG_RESPONSE, {"errors": [{"message": "name already in use"}]}],
        )
        assert res.exit_code != 0
        assert len(bodies) == 2
        assert f"repository {REPO_UUID} was added" in res.output
        assert "nothing will be scanned" in res.output
        # Both ways out are spelled out.
        assert f"policy-collection add --repository-uuid={REPO_UUID}" in res.output
        assert f"repository remove --uuid={REPO_UUID}" in res.output


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

    def test_remove_repository_cascade(self, run_query):
        res, body = run_query(
            "repository",
            ["remove", f"--uuid={REPO_UUID}", "--cascade=true"],
            response={"data": {"removeRepositoryConfig": {"removed": [], "problems": []}}},
        )
        assert body["variables"] == {"uuid": REPO_UUID, "cascade": True}

    def test_remove_repository_cascade_rejects_nonsense(self, run_queries):
        "A misspelling has to fail, not quietly leave the cascade off."
        res, bodies = run_queries(
            "repository",
            ["remove", f"--uuid={REPO_UUID}", "--cascade=treu"],
            [],
        )
        assert res.exit_code != 0
        assert "'treu' is not one of 'true', 'false'" in res.output
        assert bodies == []

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
