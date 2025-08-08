# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import textwrap
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import Mock, patch

import pytest
import requests
from click.testing import CliRunner

from stacklet.client.platform.cli import auto_configure

from .utils import BaseCliTest


class AdminCliTest(BaseCliTest):
    def test_cli_health_check(self):
        res = self.runner.invoke(self.cli, ["--help"])
        self.assertEqual(res.exit_code, 0)

    def test_admin_save_config_and_show(self):
        file_location = NamedTemporaryFile(mode="w+", delete=False)
        res = self.runner.invoke(
            self.cli,
            [
                "configure",
                "--api=baz",
                "--region=us-east-1",
                "--cognito-user-pool-id=foo",
                "--cognito-client-id=bar",
                "--idp-id=foo",
                "--auth-url=bar",
                "--cubejs=cube.local",
                f"--location={file_location.name}",
            ],
        )
        self.assertEqual(res.exit_code, 0)
        with open(file_location.name, "r") as f:
            config = json.load(f)
        self.assertEqual(config["api"], "baz")
        self.assertEqual(config["region"], "us-east-1")
        self.assertEqual(config["cognito_user_pool_id"], "foo")
        self.assertEqual(config["cognito_client_id"], "bar")
        self.assertEqual(config["idp_id"], "foo")
        self.assertEqual(config["auth_url"], "bar")
        self.assertEqual(config["cubejs"], "cube.local")

        res = self.runner.invoke(
            self.cli,
            [
                f"--config={file_location.name}",
                "show",
            ],
        )
        self.assertEqual(res.exit_code, 0)
        self.assertTrue(
            res.output.endswith(
                textwrap.dedent(
                    """\
                    api: baz
                    auth_url: bar
                    cognito_client_id: bar
                    cognito_user_pool_id: foo
                    cubejs: cube.local
                    idp_id: foo
                    region: us-east-1

                    """
                )
            )
        )

        os.unlink(file_location.name)


@pytest.fixture
def mock_config_response():
    return {
        "cognito_install": "auth.console.myorg.stacklet.io",
        "cognito_user_pool_region": "us-east-1",
        "cognito_user_pool_id": "us-east-1_ABC123",
        "cognito_user_pool_client_id": "client123",
        "cubejs_domain": "cubejs.myorg.stacklet.io",
        "saml_providers": [
            {"name": "okta", "idp_id": "okta_123"},
            {"name": "azure", "idp_id": "azure_456"},
        ],
    }


@pytest.fixture
def expected_formatted_config():
    return {
        "api": "https://api.myorg.stacklet.io",
        "auth_url": "https://auth.console.myorg.stacklet.io",
        "cognito_client_id": "client123",
        "cognito_user_pool_id": "us-east-1_ABC123",
        "cubejs": "https://cubejs.myorg.stacklet.io",
        "idp_id": "okta_123",
        "region": "us-east-1",
    }


def test_auto_configure_comprehensive(mock_config_response, expected_formatted_config):
    """Comprehensive test covering all major functionality"""
    runner = CliRunner()

    with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
        # Setup mocks
        mock_response = Mock()
        mock_response.json.return_value = mock_config_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_path = Mock(spec=Path)
        mock_parent = Mock()
        mock_path.parent = mock_parent
        mock_path.exists.return_value = False
        mock_expanduser.return_value = mock_path

        # Test with prefix URL and specific IDP
        result = runner.invoke(
            auto_configure, ["--url", "myorg", "--idp", "okta", "--location", "/test/config.json"]
        )

        assert result.exit_code == 0
        assert "Saved config to" in result.output

        # Verify requests were made to correct URLs
        assert mock_get.call_count == 2
        calls = mock_get.call_args_list
        assert "https://console.myorg.stacklet.io/config/cognito.json" in calls[0][0][0]
        assert "https://console.myorg.stacklet.io/config/cubejs.json" in calls[1][0][0]

        # Verify file operations
        mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_path.write_text.assert_called_once()
        written_config = json.loads(mock_path.write_text.call_args[0][0])
        assert written_config == expected_formatted_config


def test_url_parsing_variations(mock_config_response):
    """Test different URL input formats"""
    runner = CliRunner()

    test_cases = [
        ("myorg", "console.myorg.stacklet.io"),
        ("myorg.stacklet.io", "console.myorg.stacklet.io"),
        ("https://console.myorg.stacklet.io", "console.myorg.stacklet.io"),
        ("console.myorg.stacklet.io", "console.myorg.stacklet.io"),
    ]

    for input_url, expected_host in test_cases:
        with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
            mock_response = Mock()
            mock_response.json.return_value = {
                **mock_config_response,
                "saml_providers": [{"name": "single", "idp_id": "single_123"}],
            }
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            mock_path = Mock(spec=Path)
            mock_path.exists.return_value = True
            mock_expanduser.return_value = mock_path

            result = runner.invoke(auto_configure, ["--url", input_url])

            assert result.exit_code == 0
            # Verify the host was parsed correctly
            called_url = mock_get.call_args_list[0][0][0]
            assert expected_host in called_url


def test_single_idp_auto_selection(mock_config_response):
    """Test automatic IDP selection when only one is available"""
    runner = CliRunner()
    single_idp_config = {
        **mock_config_response,
        "saml_providers": [{"name": "single", "idp_id": "single_123"}],
    }

    with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_response = Mock()
        mock_response.json.return_value = single_idp_config
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_expanduser.return_value = mock_path

        result = runner.invoke(auto_configure, ["--url", "myorg"])

        assert result.exit_code == 0
        written_config = json.loads(mock_path.write_text.call_args[0][0])
        assert written_config["idp_id"] == "single_123"


def test_legacy_saml_config_format(mock_config_response):
    """Test handling of legacy SAML configuration format"""
    runner = CliRunner()
    legacy_config = {**mock_config_response}
    del legacy_config["saml_providers"]
    legacy_config["saml"] = {"okta_123": "okta", "azure_456": "azure"}

    with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_response = Mock()
        mock_response.json.return_value = legacy_config
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_expanduser.return_value = mock_path

        result = runner.invoke(auto_configure, ["--url", "myorg", "--idp", "okta"])

        assert result.exit_code == 0
        written_config = json.loads(mock_path.write_text.call_args[0][0])
        assert written_config["idp_id"] == "okta_123"


def test_multiple_idp_no_selection(mock_config_response):
    """Test error when multiple IDPs available but none specified"""
    runner = CliRunner()

    with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_response = Mock()
        mock_response.json.return_value = mock_config_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_expanduser.return_value = mock_path

        result = runner.invoke(auto_configure, ["--url", "myorg"])

        assert result.exit_code == 0
        assert "Multiple identity providers available" in result.output
        assert "azure, okta" in result.output


def test_unknown_idp_error(mock_config_response):
    """Test error when specified IDP is not found"""
    runner = CliRunner()

    with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_response = Mock()
        mock_response.json.return_value = mock_config_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_expanduser.return_value = mock_path

        result = runner.invoke(auto_configure, ["--url", "myorg", "--idp", "unknown"])

        assert result.exit_code == 0
        assert "Unknown identity provider 'unknown'" in result.output
        assert "known names: azure, okta" in result.output


def test_connection_error():
    """Test handling of connection errors"""
    runner = CliRunner()

    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = runner.invoke(auto_configure, ["--url", "myorg"])

        assert result.exit_code == 0
        assert "Unable to connect to" in result.output
        assert "Connection failed" in result.output


def test_http_error():
    """Test handling of HTTP errors"""
    runner = CliRunner()

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        result = runner.invoke(auto_configure, ["--url", "myorg"])

        assert result.exit_code == 0
        assert "Unable to retrieve configuration details" in result.output
        assert "404 Not Found" in result.output


def test_json_decode_error():
    """Test handling of JSON decode errors"""
    runner = CliRunner()

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "", 0)
        mock_get.return_value = mock_response

        result = runner.invoke(auto_configure, ["--url", "myorg"])

        assert result.exit_code == 0
        assert "Unable to parse configuration details" in result.output
        assert "Invalid JSON" in result.output


def test_missing_required_key_error():
    """Test handling of missing required configuration keys"""
    runner = CliRunner()

    with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_response = Mock()
        mock_response.json.return_value = {"incomplete": "config"}  # Missing required keys
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_path = Mock(spec=Path)
        mock_path.exists.return_value = True
        mock_expanduser.return_value = mock_path

        result = runner.invoke(auto_configure, ["--url", "myorg"])

        assert result.exit_code == 0
        assert "missing a required key" in result.output


def test_config_file_creation(mock_config_response):
    """Test config file and directory creation"""
    runner = CliRunner()

    with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_response = Mock()
        mock_response.json.return_value = {
            **mock_config_response,
            "saml_providers": [{"name": "single", "idp_id": "single_123"}],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Create mock path instance with all methods we need
        mock_path = Mock(spec=Path)
        mock_parent = Mock()
        mock_path.parent = mock_parent
        mock_path.exists.return_value = False
        mock_expanduser.return_value = mock_path

        result = runner.invoke(auto_configure, ["--url", "myorg"])

        assert result.exit_code == 0
        mock_parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_path.write_text.assert_called_once()

        # Verify JSON formatting
        written_json = mock_path.write_text.call_args[0][0]
        parsed_config = json.loads(written_json)
        assert isinstance(parsed_config, dict)
        # Verify it's properly formatted (indented and sorted)
        assert written_json == json.dumps(parsed_config, indent=4, sort_keys=True)


def test_existing_config_file(mock_config_response):
    """Test when config file already exists (no directory creation needed)"""
    runner = CliRunner()

    with patch("requests.get") as mock_get, patch("pathlib.Path.expanduser") as mock_expanduser:
        mock_response = Mock()
        mock_response.json.return_value = {
            **mock_config_response,
            "saml_providers": [{"name": "single", "idp_id": "single_123"}],
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        mock_path = Mock(spec=Path)
        mock_parent = Mock()
        mock_path.parent = mock_parent
        mock_path.exists.return_value = True  # File already exists
        mock_expanduser.return_value = mock_path

        result = runner.invoke(auto_configure, ["--url", "myorg"])

        assert result.exit_code == 0
        mock_parent.mkdir.assert_not_called()  # Should not create directory
        mock_path.write_text.assert_called_once()
