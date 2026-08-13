# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import re
from pathlib import Path

from stacklet.client.platform.config import JSONDict


def assert_config_has(config_file: Path, expected: JSONDict):
    """Assert configuration contains the provided values."""
    config = json.loads(config_file.read_text())
    for key, value in expected.items():
        assert config[key] == value


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def assert_query(body: JSONDict, query: str):
    """Assert GraphQL query from a response body matches ignoring spaces."""
    assert _clean(body["query"]) == _clean(query)


def assert_query_contains(body: JSONDict, fragment: str):
    """Assert a GraphQL query contains a fragment, ignoring spaces.

    For queries whose selection is too big to be worth spelling out in full.
    """
    assert _clean(fragment) in _clean(body["query"])
