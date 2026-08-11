import uuid

from .asserts import assert_query_contains


def collection_response(mutation: str, pc_uuid: str) -> dict:
    # Only a partial collection: the selection isn't what these tests are about.
    return {"data": {mutation: {"collection": {"id": "something-opaque", "uuid": pc_uuid}}}}


class TestPolicyCollection:
    def test_add_item(self, run_query):
        "Ensure that the policy version is converted properly."
        pc_uuid = str(uuid.uuid4())
        policy_uuid = str(uuid.uuid4())

        res, body = run_query(
            "policy-collection",
            [
                "add-item",
                f"--uuid={pc_uuid}",
                f"--policy-uuid={policy_uuid}",
                "--policy-version=42",
            ],
            collection_response("addPolicyCollectionItems", pc_uuid),
        )
        # Check the variable conversion.
        assert body["variables"] == {
            "uuid": pc_uuid,
            "policy_uuid": policy_uuid,
            "policy_version": 42,
        }

    def test_add_static(self, run_query):
        "Without any view options the view input collapses to an empty one."
        pc_uuid = str(uuid.uuid4())
        res, body = run_query(
            "policy-collection",
            ["add", "--name=fixed-set", "--provider=AWS"],
            collection_response("addPolicyCollection", pc_uuid),
        )
        assert body["variables"] == {"name": "fixed-set", "provider": "AWS"}
        assert_query_contains(
            body,
            """
            mutation ($name: String!, $provider: CloudProvider!) {
              addPolicyCollection(input:{
                name: $name
                provider: $provider
                repositoryView: {
                }
              }){
            """,
        )

    def test_add_dynamic(self, run_query):
        "A repository UUID plus view options makes a dynamic collection."
        pc_uuid = str(uuid.uuid4())
        repo_uuid = str(uuid.uuid4())
        res, body = run_query(
            "policy-collection",
            [
                "add",
                "--name=dynamics",
                "--provider=AWS",
                f"--repository-uuid={repo_uuid}",
                "--branch-name=main",
                "--policy-file-suffix=.yaml",
                "--policy-file-suffix=.yml",
                "--policy-directory=policies",
                "--start-rev-spec=TAIL",
            ],
            collection_response("addPolicyCollection", pc_uuid),
        )
        assert body["variables"] == {
            "name": "dynamics",
            "provider": "AWS",
            "repository_uuid": repo_uuid,
            "branch_name": "main",
            # A deep import goes over the wire as a variable, so the query builder's
            # quote stripping can't mangle it.
            "start_rev_spec": "TAIL",
            "policy_file_suffix": [".yaml", ".yml"],
            "policy_directory": ["policies"],
        }
        assert_query_contains(
            body,
            """
                repositoryUUID: $repository_uuid
                repositoryView: {
                    branchName: $branch_name
                    policyFileSuffix: $policy_file_suffix
                    policyDirectories: $policy_directory
                    startRevSpec: $start_rev_spec
                }
            """,
        )

    def test_add_auto_update_omitted(self, run_query):
        "An unset --auto-update is absent, not false: false is an error when dynamic."
        pc_uuid = str(uuid.uuid4())
        res, body = run_query(
            "policy-collection",
            ["add", "--name=c", "--provider=AWS"],
            collection_response("addPolicyCollection", pc_uuid),
        )
        assert "auto_update" not in body["variables"]
        assert "autoUpdate: $auto_update" not in body["query"]

    def test_add_auto_update_given(self, run_query):
        pc_uuid = str(uuid.uuid4())
        res, body = run_query(
            "policy-collection",
            ["add", "--name=c", "--provider=AWS", "--auto-update=true"],
            collection_response("addPolicyCollection", pc_uuid),
        )
        assert body["variables"]["auto_update"] is True
        assert_query_contains(body, "$auto_update: Boolean!")

    def test_add_view_option_without_repository(self, run_queries):
        "View options are meaningless without a repository, so say so up front."
        res, bodies = run_queries(
            "policy-collection",
            ["add", "--name=c", "--provider=AWS", "--branch-name=main"],
            [],
        )
        assert res.exit_code != 0
        assert "--branch-name only applies to a dynamic policy collection" in res.output
        assert "--repository-uuid" in res.output
        # Rejected before anything was sent.
        assert bodies == []

    def test_update_view(self, run_query):
        "Update takes the view options, minus the add-only start revision."
        pc_uuid = str(uuid.uuid4())
        res, body = run_query(
            "policy-collection",
            ["update", f"--uuid={pc_uuid}", "--branch-name=release"],
            collection_response("updatePolicyCollection", pc_uuid),
        )
        assert body["variables"] == {"uuid": pc_uuid, "branch_name": "release"}
        assert_query_contains(
            body,
            """
                repositoryView: {
                    branchName: $branch_name
                }
            """,
        )
        assert "startRevSpec" not in body["query"]
