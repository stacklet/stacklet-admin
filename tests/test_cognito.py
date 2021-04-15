from unittest import TestCase

import boto3
from click.testing import CliRunner
from moto import mock_cognitoidp

from cli.cli import cli
from cli.cognito import CognitoUserManager
from cli.context import StackletContext


class CognitoUserManagerTest(TestCase):

    runner = CliRunner()
    cli = cli

    mock_cognitoidp = mock_cognitoidp()
    region = "us-east-1"

    def setUp(self):
        self.mock_cognitoidp.start()
        self.client = boto3.client("cognito-idp", region_name=self.region)
        resp = self.client.create_user_pool(PoolName="stackpool")
        self.cognito_user_pool_id = resp["UserPool"]["Id"]

        resp = self.client.create_user_pool_client(
            UserPoolId=self.cognito_user_pool_id, ClientName="stackpool-client"
        )
        self.cognito_client_id = resp["UserPoolClient"]["ClientId"]

    def tearDown(self):
        self.mock_cognitoidp.stop()

    def test_cognito_user_manager_create_user(self):
        config = dict(
            api="mock://stacklet.acme.org/api",
            cognito_user_pool_id=self.cognito_user_pool_id,
            cognito_client_id=self.cognito_client_id,
            region=self.region,
        )
        users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
        self.assertEqual(len(users["Users"]), 0)

        with StackletContext(raw_config=config) as context:
            manager = CognitoUserManager.from_context(context)
            manager.create_user(
                user="test-user",
                password="Foobar123!",
                email="foo@acme.org",
                phone_number="+15551234567",
            )
            users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
            self.assertEqual(users["Users"][0]["Username"], "test-user")

            # creating a user is an idempotent action, this should return true without
            # raising an error
            res = manager.create_user(
                user="test-user",
                password="Foobar123!",
                email="foo@acme.org",
                phone_number="+15551234567",
            )
            self.assertTrue(res)
            users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
            self.assertEqual(users["Users"][0]["Username"], "test-user")

    def test_cognito_create_user_cli(self):
        res = self.runner.invoke(
            self.cli,
            [
                "admin",
                "--api=mock://stacklet.acme.org/api",
                f"--cognito-region={self.region}",
                f"--cognito-user-pool-id={self.cognito_user_pool_id}",
                f"--cognito-client-id={self.cognito_client_id}",
                "create-user",
                "--username=test-user",
                "--password=Foobar123!",
                "--email=foo@acme.org",
                "--phone-number=+15551234567",
            ],
        )
        self.assertEqual(res.exit_code, 0)

        users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
        self.assertEqual(users["Users"][0]["Username"], "test-user")
