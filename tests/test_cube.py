# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests_mock

from stacklet.client.platform.commands.cube import _request
from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.exceptions import MissingToken


class TestCubeJS:
    def test_missing_token(self, sample_config_file):
        """Test that cubejs command raises an error when credentials are not configured."""
        context = StackletContext(config_file=sample_config_file)
        with pytest.raises(MissingToken):
            _request(context, "GET", "v1/meta")

    def test_request_with_token(self, requests_adapter, sample_config_file, api_token_in_file):
        """Test that cubejs request works with valid token."""
        context = StackletContext(config_file=sample_config_file)

        expected_response = {"cubes": [{"name": "TestCube"}]}
        requests_adapter.register_uri(
            "GET",
            "mock://cubejs.stacklet.acme.org/cubejs-api/v1/meta",
            json=expected_response,
        )

        result = _request(context, "GET", "v1/meta")
        assert result == expected_response

    def test_cubejs_meta_command(
        self, requests_adapter, sample_config_file, invoke_cli, api_token_in_file
    ):
        """Test cubejs meta command through CLI."""
        expected_response = {
            "cubes": [
                {
                    "name": "TestCube",
                    "measures": [],
                    "dimensions": [],
                }
            ]
        }
        requests_adapter.get(requests_mock.ANY, json=expected_response)

        res = invoke_cli("cubejs", "meta")
        assert res.exit_code == 0
        assert "TestCube" in res.output
