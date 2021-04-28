import json
import os
from tempfile import NamedTemporaryFile

from utils import BaseCliTest


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
                "--local-cert=foo",
                "--local-cert-key=bar",
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
        self.assertEqual(config["local_cert"], "foo")
        self.assertEqual(config["local_cert_key"], "bar")

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
                "api: baz\nauth_url: bar\ncognito_client_id: bar\ncognito_user_pool_id: foo\nidp_id: foo\nlocal_cert: foo\nlocal_cert_key: bar\nregion: us-east-1\n\n"  # noqa
            )
        )
        os.unlink(file_location.name)
