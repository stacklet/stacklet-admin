# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import textwrap
from tempfile import NamedTemporaryFile

import requests

from .utils import BaseCliTest


class TestAdminCli(BaseCliTest):
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

    def test_auto_configure_url_only(self):
        """Test auto-configure with --url parameter"""
        file_location = NamedTemporaryFile(mode="w+", delete=False)

        # Mock the HTTP responses for config endpoints
        mock_config = {
            "cognito_install": "auth.console.dev.stacklet.dev",
            "cognito_user_pool_region": "us-east-2",
            "cognito_user_pool_id": "us-east-2_test123",
            "cognito_user_pool_client_id": "test-client-id",
            "cubejs_domain": "cubejs.dev.stacklet.dev",
            "saml_providers": [{"name": "TestIDP", "idp_id": "test-idp-id"}],
        }

        self.adapter.get("https://console.dev.stacklet.dev/config/cognito.json", json=mock_config)
        self.adapter.get("https://console.dev.stacklet.dev/config/cubejs.json", json={})

        res = self.runner.invoke(
            self.cli,
            [
                "auto-configure",
                "--url=console.dev.stacklet.dev",
                f"--location={file_location.name}",
            ],
        )

        self.assertEqual(res.exit_code, 0)

        with open(file_location.name, "r") as f:
            config = json.load(f)

        self.assertEqual(config["api"], "https://api.dev.stacklet.dev")
        self.assertEqual(config["auth_url"], "https://auth.console.dev.stacklet.dev")
        self.assertEqual(config["cognito_client_id"], "test-client-id")
        self.assertEqual(config["cognito_user_pool_id"], "us-east-2_test123")
        self.assertEqual(config["region"], "us-east-2")
        self.assertEqual(config["cubejs"], "https://cubejs.dev.stacklet.dev")
        self.assertEqual(config["idp_id"], "test-idp-id")

        os.unlink(file_location.name)

    def test_auto_configure_prefix_only(self):
        """Test auto-configure with --prefix parameter"""
        file_location = NamedTemporaryFile(mode="w+", delete=False)

        mock_config = {
            "cognito_install": "auth.console.myorg.stacklet.io",
            "cognito_user_pool_region": "us-west-2",
            "cognito_user_pool_id": "us-west-2_test456",
            "cognito_user_pool_client_id": "test-client-id-2",
            "cubejs_domain": "cubejs.myorg.stacklet.io",
            "saml_providers": [{"name": "OrgIDP", "idp_id": "org-idp-id"}],
        }

        self.adapter.get("https://console.myorg.stacklet.io/config/cognito.json", json=mock_config)
        self.adapter.get("https://console.myorg.stacklet.io/config/cubejs.json", json={})

        res = self.runner.invoke(
            self.cli,
            [
                "auto-configure",
                "--prefix=myorg",
                f"--location={file_location.name}",
            ],
        )

        self.assertEqual(res.exit_code, 0)

        with open(file_location.name, "r") as f:
            config = json.load(f)

        self.assertEqual(config["api"], "https://api.myorg.stacklet.io")
        self.assertEqual(config["auth_url"], "https://auth.console.myorg.stacklet.io")
        self.assertEqual(config["cubejs"], "https://cubejs.myorg.stacklet.io")

        os.unlink(file_location.name)

    def test_auto_configure_url_without_console_prefix(self):
        """Test auto-configure with URL that needs console prefix added"""
        file_location = NamedTemporaryFile(mode="w+", delete=False)

        mock_config = {
            "cognito_install": "auth.console.example.stacklet.io",
            "cognito_user_pool_region": "eu-west-1",
            "cognito_user_pool_id": "eu-west-1_test789",
            "cognito_user_pool_client_id": "test-client-id-3",
            "cubejs_domain": "cubejs.example.stacklet.io",
            "saml_providers": [{"name": "ExampleIDP", "idp_id": "example-idp-id"}],
        }

        self.adapter.get(
            "https://console.example.stacklet.io/config/cognito.json", json=mock_config
        )
        self.adapter.get("https://console.example.stacklet.io/config/cubejs.json", json={})

        res = self.runner.invoke(
            self.cli,
            [
                "auto-configure",
                "--url=example.stacklet.io",  # Missing console prefix
                f"--location={file_location.name}",
            ],
        )

        self.assertEqual(res.exit_code, 0)

        with open(file_location.name, "r") as f:
            config = json.load(f)

        self.assertEqual(config["region"], "eu-west-1")
        self.assertEqual(config["cognito_user_pool_id"], "eu-west-1_test789")

        os.unlink(file_location.name)

    def test_auto_configure_both_url_and_prefix_error(self):
        """Test that providing both --url and --prefix results in an error"""
        res = self.runner.invoke(
            self.cli,
            [
                "auto-configure",
                "--url=console.dev.stacklet.dev",
                "--prefix=dev",
            ],
        )

        self.assertEqual(res.exit_code, 1)  # Command should exit with error code
        self.assertIn("Cannot specify both --url and --prefix", res.output)

    def test_auto_configure_neither_url_nor_prefix_error(self):
        """Test that providing neither --url nor --prefix results in an error"""
        res = self.runner.invoke(
            self.cli,
            [
                "auto-configure",
            ],
        )

        self.assertEqual(res.exit_code, 1)  # Command should exit with error code
        self.assertIn("Must specify either --url or --prefix", res.output)

    def test_auto_configure_connection_error(self):
        """Test auto-configure behavior when connection fails"""
        file_location = NamedTemporaryFile(mode="w+", delete=False)

        self.adapter.get(
            "https://console.nonexistent.stacklet.dev/config/cognito.json",
            exc=requests.exceptions.ConnectionError,
        )

        res = self.runner.invoke(
            self.cli,
            [
                "auto-configure",
                "--url=console.nonexistent.stacklet.dev",
                f"--location={file_location.name}",
            ],
        )

        self.assertEqual(res.exit_code, 1)
        self.assertIn("Unable to connect to", res.output)

        os.unlink(file_location.name)

    def test_auto_configure_multiple_idps_with_selection(self):
        """Test auto-configure with multiple IDPs and explicit selection"""
        file_location = NamedTemporaryFile(mode="w+", delete=False)

        mock_config = {
            "cognito_install": "auth.console.multi.stacklet.dev",
            "cognito_user_pool_region": "us-east-1",
            "cognito_user_pool_id": "us-east-1_multi123",
            "cognito_user_pool_client_id": "multi-client-id",
            "cubejs_domain": "cubejs.multi.stacklet.dev",
            "saml_providers": [
                {"name": "IDP1", "idp_id": "idp-1"},
                {"name": "IDP2", "idp_id": "idp-2"},
            ],
        }

        self.adapter.get("https://console.multi.stacklet.dev/config/cognito.json", json=mock_config)
        self.adapter.get("https://console.multi.stacklet.dev/config/cubejs.json", json={})

        res = self.runner.invoke(
            self.cli,
            [
                "auto-configure",
                "--url=console.multi.stacklet.dev",
                "--idp=IDP2",
                f"--location={file_location.name}",
            ],
        )

        self.assertEqual(res.exit_code, 0)

        with open(file_location.name, "r") as f:
            config = json.load(f)

        self.assertEqual(config["idp_id"], "idp-2")

        os.unlink(file_location.name)

    def test_auto_configure_multiple_idps_no_selection_error(self):
        """Test auto-configure with multiple IDPs but no selection results in error"""
        mock_config = {
            "cognito_install": "auth.console.multi.stacklet.dev",
            "cognito_user_pool_region": "us-east-1",
            "cognito_user_pool_id": "us-east-1_multi123",
            "cognito_user_pool_client_id": "multi-client-id",
            "cubejs_domain": "cubejs.multi.stacklet.dev",
            "saml_providers": [
                {"name": "IDP1", "idp_id": "idp-1"},
                {"name": "IDP2", "idp_id": "idp-2"},
            ],
        }

        self.adapter.get("https://console.multi.stacklet.dev/config/cognito.json", json=mock_config)
        self.adapter.get("https://console.multi.stacklet.dev/config/cubejs.json", json={})

        res = self.runner.invoke(
            self.cli,
            [
                "auto-configure",
                "--url=console.multi.stacklet.dev",
            ],
        )

        self.assertEqual(res.exit_code, 1)
        self.assertIn("Multiple identity providers available", res.output)
