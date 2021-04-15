import json
import os

from click.testing import CliRunner
from tempfile import NamedTemporaryFile
from unittest import TestCase

from cli.cli import cli


class AdminCliTest(TestCase):

    runner = CliRunner()
    cli = cli

    def test_cli_health_check(self):
        res = self.runner.invoke(self.cli, ['--help'])
        self.assertEqual(res.exit_code, 0)

    def test_admin_save_config_and_show(self):
        file_location = NamedTemporaryFile(
            mode='w+',
            delete=False
        )
        res = self.runner.invoke(
            self.cli,
            [
                'admin',
                'configure',
                '--api=baz',
                '--region=us-east-1',
                '--cognito-user-pool-id=foo',
                '--cognito-client-id=bar',
                f'--location={file_location.name}',
            ]
        )
        self.assertEqual(res.exit_code, 0)
        with open(file_location.name, 'r') as f:
            config = json.load(f)
        self.assertEqual(config['api'], 'baz')
        self.assertEqual(config['region'], 'us-east-1')
        self.assertEqual(config['cognito_user_pool_id'], 'foo')
        self.assertEqual(config['cognito_client_id'], 'bar')

        res = self.runner.invoke(
            self.cli,
            [
                'admin',
                f'--config={file_location.name}',
                'show',
            ]
        )
        self.assertEqual(res.exit_code, 0)
        self.assertEqual(
            "api: baz\ncognito_client_id: bar\ncognito_user_pool_id: foo\nregion: us-east-1\n\n",
            res.output
        )
        os.unlink(file_location.name)
