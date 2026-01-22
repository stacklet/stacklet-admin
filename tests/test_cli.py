# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import textwrap

import requests

from .asserts import assert_config_has


class TestAdminCli:
    def test_cli_health_check(self, invoke_cli):
        res = invoke_cli("--help", with_config=False)
        assert res.exit_code == 0

    def test_admin_save_config_and_show(self, config_file, invoke_cli):
        res = invoke_cli(
            "configure",
            "--api=baz",
            "--region=us-east-1",
            "--cognito-user-pool-id=foo",
            "--cognito-client-id=bar",
            "--idp-id=foo",
            "--auth-url=bar",
            "--cubejs=cube.local",
            f"--location={config_file}",
            with_config=False,
        )
        assert res.exit_code == 0
        assert_config_has(
            config_file,
            {
                "api": "baz",
                "region": "us-east-1",
                "cognito_user_pool_id": "foo",
                "cognito_client_id": "bar",
                "idp_id": "foo",
                "auth_url": "bar",
                "cubejs": "cube.local",
            },
        )

        res = invoke_cli("show")
        assert res.exit_code == 0
        assert res.output.endswith(
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

    def test_auto_configure_url_only(self, config_file, requests_adapter, invoke_cli):
        config = {
            "cognito_install": "auth.console.dev.stacklet.dev",
            "cognito_user_pool_region": "us-east-2",
            "cognito_user_pool_id": "us-east-2_test123",
            "cognito_user_pool_client_id": "test-client-id",
            "cubejs_domain": "cubejs.dev.stacklet.dev",
            "saml_providers": [{"name": "TestIDP", "idp_id": "test-idp-id"}],
        }

        requests_adapter.get("https://console.dev.stacklet.dev/config/cognito.json", json=config)
        requests_adapter.get("https://console.dev.stacklet.dev/config/cubejs.json", json={})

        res = invoke_cli(
            "auto-configure",
            "--url=console.dev.stacklet.dev",
            f"--location={config_file}",
            with_config=False,
        )

        assert res.exit_code == 0
        assert_config_has(
            config_file,
            {
                "api": "https://api.dev.stacklet.dev",
                "auth_url": "https://auth.console.dev.stacklet.dev",
                "cognito_client_id": "test-client-id",
                "cognito_user_pool_id": "us-east-2_test123",
                "region": "us-east-2",
                "cubejs": "https://cubejs.dev.stacklet.dev",
                "idp_id": "test-idp-id",
            },
        )

    def test_auto_configure_prefix_only(self, config_file, requests_adapter, invoke_cli):
        config = {
            "cognito_install": "auth.console.myorg.stacklet.io",
            "cognito_user_pool_region": "us-west-2",
            "cognito_user_pool_id": "us-west-2_test456",
            "cognito_user_pool_client_id": "test-client-id-2",
            "cubejs_domain": "cubejs.myorg.stacklet.io",
            "saml_providers": [{"name": "OrgIDP", "idp_id": "org-idp-id"}],
        }

        requests_adapter.get("https://console.myorg.stacklet.io/config/cognito.json", json=config)
        requests_adapter.get("https://console.myorg.stacklet.io/config/cubejs.json", json={})

        res = invoke_cli(
            "auto-configure",
            "--prefix=myorg",
            f"--location={config_file}",
            with_config=False,
        )

        assert res.exit_code == 0
        assert_config_has(
            config_file,
            {
                "api": "https://api.myorg.stacklet.io",
                "auth_url": "https://auth.console.myorg.stacklet.io",
                "cubejs": "https://cubejs.myorg.stacklet.io",
            },
        )

    def test_auto_configure_url_without_console_prefix(
        self, config_file, requests_adapter, invoke_cli
    ):
        config = {
            "cognito_install": "auth.console.example.stacklet.io",
            "cognito_user_pool_region": "eu-west-1",
            "cognito_user_pool_id": "eu-west-1_test789",
            "cognito_user_pool_client_id": "test-client-id-3",
            "cubejs_domain": "cubejs.example.stacklet.io",
            "saml_providers": [{"name": "ExampleIDP", "idp_id": "example-idp-id"}],
        }

        requests_adapter.get("https://console.example.stacklet.io/config/cognito.json", json=config)
        requests_adapter.get("https://console.example.stacklet.io/config/cubejs.json", json={})

        res = invoke_cli(
            "auto-configure",
            "--url=example.stacklet.io",
            f"--location={config_file}",
            with_config=False,
        )

        assert res.exit_code == 0
        assert_config_has(
            config_file,
            {
                "region": "eu-west-1",
                "cognito_user_pool_id": "eu-west-1_test789",
            },
        )

    def test_auto_configure_both_url_and_prefix_error(self, invoke_cli):
        res = invoke_cli(
            "auto-configure",
            "--url=console.dev.stacklet.dev",
            "--prefix=dev",
            with_config=False,
        )

        assert res.exit_code == 1
        assert "Cannot specify both --url and --prefix" in res.output

    def test_auto_configure_neither_url_nor_prefix_error(self, invoke_cli):
        res = invoke_cli(
            "auto-configure",
            with_config=False,
        )

        assert res.exit_code == 1
        assert "Must specify either --url or --prefix" in res.output

    def test_auto_configure_connection_error(self, config_file, requests_adapter, invoke_cli):
        requests_adapter.get(
            "https://console.nonexistent.stacklet.dev/config/cognito.json",
            exc=requests.exceptions.ConnectionError,
        )

        res = invoke_cli(
            "auto-configure",
            "--url=console.nonexistent.stacklet.dev",
            f"--location={config_file}",
            with_config=False,
        )

        assert res.exit_code == 1
        assert "Unable to connect to" in res.output

    def test_auto_configure_multiple_idps_with_selection(
        self, config_file, requests_adapter, invoke_cli
    ):
        config = {
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

        requests_adapter.get("https://console.multi.stacklet.dev/config/cognito.json", json=config)
        requests_adapter.get("https://console.multi.stacklet.dev/config/cubejs.json", json={})

        res = invoke_cli(
            "auto-configure",
            "--url=console.multi.stacklet.dev",
            "--idp=IDP2",
            f"--location={config_file}",
            with_config=False,
        )

        assert res.exit_code == 0
        assert_config_has(
            config_file,
            {
                "idp_id": "idp-2",
            },
        )

    def test_auto_configure_multiple_idps_no_selection_error(self, requests_adapter, invoke_cli):
        config = {
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

        requests_adapter.get("https://console.multi.stacklet.dev/config/cognito.json", json=config)
        requests_adapter.get("https://console.multi.stacklet.dev/config/cubejs.json", json={})

        res = invoke_cli(
            "auto-configure",
            "--url=console.multi.stacklet.dev",
            with_config=False,
        )

        assert res.exit_code == 1
        assert "Multiple identity providers available" in res.output
