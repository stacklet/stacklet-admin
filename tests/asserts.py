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


def assert_query(body: JSONDict, query: str):
    """Assert GraphQL query from a response body matches ignorning spaces."""
    space_re = re.compile(r"\s+")

    def clean(s):
        return space_re.sub(" ", s).strip()

    assert clean(body["query"]) == clean(query)
