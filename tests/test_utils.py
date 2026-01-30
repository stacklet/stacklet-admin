# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest

from stacklet.client.platform.formatter import (
    JSONFormatter,
    RawFormatter,
    YAMLFormatter,
)
from stacklet.client.platform.utils import get_log_level


class TestUtils:
    @pytest.mark.parametrize(
        "verbosity,level",
        [
            (-9999, 50),
            (0, 40),
            (1, 30),
            (2, 20),
            (3, 10),
            (4, 0),
            (5, 0),
            (6, 0),
            (9999, 0),
        ],
    )
    def test_get_log_level(self, verbosity, level):
        assert get_log_level(verbosity) == level

    @pytest.mark.parametrize(
        "formatter,expected_output",
        [
            (RawFormatter, "{'foo': 'bar'}"),
            (JSONFormatter, '{\n  "foo": "bar"\n}'),
            (YAMLFormatter, "foo: bar\n"),
        ],
    )
    def test_formatters(self, formatter, expected_output):
        input_data = {"foo": "bar"}
        result = formatter()(input_data)
        assert result == expected_output
