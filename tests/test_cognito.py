import boto3
import pytest
from click.testing import CliRunner
from moto import mock_cognitoidp

from stacklet.client.platform.cli import cli
from stacklet.client.platform.cognito import CognitoUserManager
from stacklet.client.platform.context import StackletContext


class TestCognitoUserManager:

    runner = CliRunner()
    cli = cli

    region = "us-east-1"

    @pytest.fixture(autouse=True)
    def mock_cognito(self):
        with mock_cognitoidp():
            self.client = boto3.client("cognito-idp", region_name=self.region)
            resp = self.client.create_user_pool(PoolName="stackpool")
            self.cognito_user_pool_id = resp["UserPool"]["Id"]

            resp = self.client.create_user_pool_client(
                UserPoolId=self.cognito_user_pool_id, ClientName="stackpool-client"
            )
            self.cognito_client_id = resp["UserPoolClient"]["ClientId"]
            yield

    @pytest.fixture
    def admin_group(self):
        r = self.client.create_group(
            GroupName='admin',
            UserPoolId=self.cognito_user_pool_id,
        )
        yield r["Group"]["GroupName"]

    @pytest.fixture
    def new_user(self):
        r = self.client.admin_create_user(
            UserPoolId=self.cognito_user_pool_id,
            Username="test",
        )
        yield r["User"]["Username"]

    def test_cognito_user_manager_create_user(self):
        config = dict(
            api="mock://stacklet.acme.org/api",
            cognito_user_pool_id=self.cognito_user_pool_id,
            cognito_client_id=self.cognito_client_id,
            region=self.region,
        )
        users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
        assert len(users["Users"]) == 0

        with StackletContext(raw_config=config) as context:
            manager = CognitoUserManager.from_context(context)
            manager.create_user(
                user="test-user",
                password="Foobar123!",
                email="foo@acme.org",
                phone_number="+15551234567",
            )
            users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
            assert users["Users"][0]["Username"] == "test-user"

            # creating a user is an idempotent action, this should return true without
            # raising an error
            res = manager.create_user(
                user="test-user",
                password="Foobar123!",
                email="foo@acme.org",
                phone_number="+15551234567",
            )
            assert res is True
            users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
            assert users["Users"][0]["Username"] == "test-user"

    def default_args(self) -> list[str]:
        return [
            "--api=mock://stacklet.acme.org/api",
            f"--cognito-region={self.region}",
            f"--cognito-user-pool-id={self.cognito_user_pool_id}",
            f"--cognito-client-id={self.cognito_client_id}",
        ]

    def test_cognito_create_user_cli(self):
        res = self.runner.invoke(
            self.cli,
            self.default_args() +
            [
                "user",
                "add",
                "--username=test-user",
                "--password=Foobar123!",
                "--email=foo@acme.org",
                "--phone-number=+15551234567",
            ],
        )
        assert res.exit_code ==  0

        users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
        assert users["Users"][0]["Username"] == "test-user"

    def get_user_groups(self, username):
        result = self.client.admin_list_groups_for_user(
            Username=username,
            UserPoolId=self.cognito_user_pool_id,
        )
        return [group["GroupName"] for group in result["Groups"]]

    def test_ensure_group_missing_group(self, new_user):
        res = self.runner.invoke(
            self.cli,
            self.default_args() +
            [
                "user",
                "ensure-group",
                f"--username={new_user}",
                "--group=missing",
            ],
        )
        assert res.exit_code ==  0
        # Since the group wasn't there, it isn't there...
        assert self.get_user_groups(new_user) == []

    def test_ensure_group_existing_group(self, new_user, admin_group):
        res = self.runner.invoke(
            self.cli,
            self.default_args() +
            [
                "user",
                "ensure-group",
                f"--username={new_user}",
                f"--group={admin_group}",
            ],
        )
        assert res.exit_code ==  0
        # Since the group wasn't there, it isn't there...
        assert self.get_user_groups(new_user) == [admin_group]
