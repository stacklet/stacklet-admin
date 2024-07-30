import uuid

from .utils import BaseCliTest, JSONDict


class TestPolicyCollection(BaseCliTest):
    def test_add_item(self):
        "Ensure that the policy version is converted properly."
        pc_uuid = str(uuid.uuid4())
        policy_uuid = str(uuid.uuid4())

        # Only giving a partial response because that isn't what we're testing.
        response = JSONDict(
            data={
                "addPolicyCollectionItems": {
                    "collection": {"id": "something-opaque", "uuid": pc_uuid}
                }
            }
        )
        res, body = self.run_query(
            "policy-collection",
            [
                "add-item",
                f"--uuid={pc_uuid}",
                f"--policy-uuid={policy_uuid}",
                "--policy-version=42",
            ],
            response,
        )
        # Check the variable conversion.
        assert body["variables"] == {
            "uuid": pc_uuid,
            "policy_uuid": policy_uuid,
            "policy_version": 42,
        }
