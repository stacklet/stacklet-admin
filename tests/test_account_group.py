# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json

from .asserts import assert_query


class TestAccountGroup:
    def test_add_item(self, run_query):
        res, body = run_query(
            "account-group",
            [
                "add-item",
                "--uuid=11111111-1111-1111-1111-111111111111",
                "--key=123456789012",
            ],
            response={
                "data": {
                    "upsertAccountGroupMappings": {
                        "mappings": [
                            {
                                "id": "mapping:1",
                                "regions": None,
                                "account": {
                                    "key": "123456789012",
                                    "provider": "AWS",
                                    "name": "test-account",
                                },
                                "group": {
                                    "uuid": "11111111-1111-1111-1111-111111111111",
                                    "name": "test-group",
                                },
                            }
                        ]
                    }
                }
            },
        )
        assert res.exit_code == 0
        assert_query(
            body,
            """
            mutation ($uuid: String!, $key: String!) {
              upsertAccountGroupMappings(input:{
                mappings: [
                    {
                        accountKey: $key
                        groupUUID: $uuid
                    }
                ]
              }) {
                  mappings {
                    id
                    regions
                    account {
                        key
                        provider
                        name
                    }
                    group {
                        uuid
                        name
                    }
                }
              }
          }
            """,
        )
        assert body["variables"] == {
            "uuid": "11111111-1111-1111-1111-111111111111",
            "key": "123456789012",
        }

    def test_remove_item(self, requests_adapter, sample_config_file, api_token_in_file, invoke_cli):
        """removeAccountGroupMappings needs a mapping id, so removal is a lookup then a mutation."""
        requests_adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            [
                {
                    "json": {
                        "data": {
                            "accountGroup": {
                                "accountMappings": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": "mapping:1",
                                                "account": {
                                                    "key": "123456789012",
                                                    "provider": "AWS",
                                                },
                                            }
                                        }
                                    ],
                                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                                }
                            }
                        }
                    }
                },
                {
                    "json": {
                        "data": {"removeAccountGroupMappings": {"removed": [{"id": "mapping:1"}]}}
                    }
                },
            ],
        )

        res = invoke_cli(
            "account-group",
            "remove-item",
            "--uuid=11111111-1111-1111-1111-111111111111",
            "--key=123456789012",
            "--provider=AWS",
        )
        assert res.exit_code == 0, res.output

        requests = [json.loads(r.body.decode()) for r in requests_adapter.request_history]
        assert len(requests) == 2

        assert_query(
            requests[0],
            """
            query ($uuid: String!) {
              accountGroup(uuid: $uuid) {
                accountMappings(
                    first: 1000
                ) {
                    edges {
                        node {
                            id
                            account {
                                key
                                provider
                            }
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
              }
          }
            """,
        )
        assert requests[0]["variables"] == {"uuid": "11111111-1111-1111-1111-111111111111"}

        assert_query(
            requests[1],
            """
            mutation ($mapping_id: ID!) {
              removeAccountGroupMappings(input:{
                ids: [$mapping_id]
              }) {
                  removed {
                    id
                }
              }
          }
            """,
        )
        assert requests[1]["variables"] == {"mapping_id": "mapping:1"}

    def test_remove_item_paginates(
        self, requests_adapter, sample_config_file, api_token_in_file, invoke_cli
    ):
        """The lookup must page through accountMappings, not just the first page."""
        requests_adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            [
                {
                    "json": {
                        "data": {
                            "accountGroup": {
                                "accountMappings": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": "mapping:1",
                                                "account": {
                                                    "key": "111111111111",
                                                    "provider": "AWS",
                                                },
                                            }
                                        }
                                    ],
                                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                                }
                            }
                        }
                    }
                },
                {
                    "json": {
                        "data": {
                            "accountGroup": {
                                "accountMappings": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": "mapping:2",
                                                "account": {
                                                    "key": "222222222222",
                                                    "provider": "AWS",
                                                },
                                            }
                                        }
                                    ],
                                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                                }
                            }
                        }
                    }
                },
                {
                    "json": {
                        "data": {"removeAccountGroupMappings": {"removed": [{"id": "mapping:2"}]}}
                    }
                },
            ],
        )

        res = invoke_cli(
            "account-group",
            "remove-item",
            "--uuid=11111111-1111-1111-1111-111111111111",
            "--key=222222222222",
            "--provider=AWS",
        )
        assert res.exit_code == 0, res.output

        requests = [json.loads(r.body.decode()) for r in requests_adapter.request_history]
        assert len(requests) == 3
        assert requests[0]["variables"] == {"uuid": "11111111-1111-1111-1111-111111111111"}
        assert requests[1]["variables"] == {
            "uuid": "11111111-1111-1111-1111-111111111111",
            "after": "cursor-1",
        }
        assert requests[2]["variables"] == {"mapping_id": "mapping:2"}

    def test_remove_item_not_found(
        self, requests_adapter, sample_config_file, api_token_in_file, invoke_cli
    ):
        requests_adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json={"data": {"accountGroup": {"accountMappings": {"edges": []}}}},
        )

        res = invoke_cli(
            "account-group",
            "remove-item",
            "--uuid=11111111-1111-1111-1111-111111111111",
            "--key=123456789012",
            "--provider=AWS",
        )
        assert res.exit_code != 0
        assert "No account with key" in res.output
