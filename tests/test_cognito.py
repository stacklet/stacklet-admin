# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json

import boto3
import pytest
from moto import mock_aws

from stacklet.client.platform.cognito import CognitoUserManager
from stacklet.client.platform.context import StackletContext


class TestCognitoUserManager:
    region = "us-east-1"

    @pytest.fixture(autouse=True)
    def _setup(self, config_file):
        with mock_aws():
            self.client = boto3.client("cognito-idp", region_name=self.region)
            resp = self.client.create_user_pool(PoolName="stackpool")
            self.cognito_user_pool_id = resp["UserPool"]["Id"]

            resp = self.client.create_user_pool_client(
                UserPoolId=self.cognito_user_pool_id, ClientName="stackpool-client"
            )
            self.cognito_client_id = resp["UserPoolClient"]["ClientId"]

            # write the custom config to file so CLI can find it
            config = {
                "api": "mock://stacklet.acme.org/api",
                "cognito_user_pool_id": self.cognito_user_pool_id,
                "cognito_client_id": self.cognito_client_id,
                "region": self.region,
                "cubejs": "mock://cubejs.stacklet.acme.org/api",
            }
            config_file.write_text(json.dumps(config))

            yield

    @pytest.fixture
    def admin_group(self):
        r = self.client.create_group(
            GroupName="admin",
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

    def get_user_groups(self, username):
        result = self.client.admin_list_groups_for_user(
            Username=username,
            UserPoolId=self.cognito_user_pool_id,
        )
        return [group["GroupName"] for group in result["Groups"]]

    def test_cognito_user_manager_create_user(self, config_file):
        users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
        assert len(users["Users"]) == 0

        context = StackletContext(config_file=config_file)
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

    def test_cognito_create_user_cli(self, invoke_cli):
        res = invoke_cli(
            "user",
            "add",
            "--username=test-user",
            "--password=Foobar123!",
            "--email=foo@acme.org",
            "--phone-number=+15551234567",
        )
        assert res.exit_code == 0

        users = self.client.list_users(UserPoolId=self.cognito_user_pool_id)
        assert users["Users"][0]["Username"] == "test-user"

    def test_ensure_group_missing_group(self, new_user, invoke_cli):
        res = invoke_cli(
            "user",
            "ensure-group",
            f"--username={new_user}",
            "--group=missing",
        )
        assert res.exit_code == 1
        assert self.get_user_groups(new_user) == []

    def test_ensure_group_existing_group(self, new_user, admin_group, invoke_cli):
        res = invoke_cli(
            "user",
            "ensure-group",
            f"--username={new_user}",
            f"--group={admin_group}",
        )
        assert res.exit_code == 0
        assert self.get_user_groups(new_user) == [admin_group]

    def test_ensure_group_already_in_group(self, new_user, admin_group, invoke_cli):
        self.client.admin_add_user_to_group(
            UserPoolId=self.cognito_user_pool_id,
            Username=new_user,
            GroupName=admin_group,
        )
        assert self.get_user_groups(new_user) == [admin_group]

        res = invoke_cli(
            "user",
            "ensure-group",
            f"--username={new_user}",
            f"--group={admin_group}",
        )
        assert res.exit_code == 0
        assert self.get_user_groups(new_user) == [admin_group]
