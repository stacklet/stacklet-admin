# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any
from unittest import TestCase
from unittest.mock import MagicMock, patch

import requests_mock
from click.testing import CliRunner, Result

from stacklet.client.platform.cli import cli
from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.executor import StackletGraphqlExecutor

JSONDict = dict[str, Any]


def get_mock_context():
    mock_ctx = MagicMock()
    mock_ctx.config = {
        "config": None,
        "output": "yaml",
        "page_variables": {"first": 20, "last": 20, "before": "", "after": ""},
        "raw_config": {
            "cognito_user_pool_id": "foo",
            "cognito_client_id": "bar",
            "region": "us-east-1",
            "api": "https://stacklet.acme.org/api",
        },
    }
    return mock_ctx


def get_executor_adapter():
    context = StackletContext(
        raw_config={
            "cognito_user_pool_id": "foo",
            "cognito_client_id": "bar",
            "region": "us-east-1",
            "api": "mock://stacklet.acme.org/api",
        }
    )
    executor = StackletGraphqlExecutor(context=context, token="foo")
    adapter = requests_mock.Adapter()
    executor.session.mount("mock://", adapter)
    return executor, adapter


class BaseCliTest(TestCase):
    """
    Base Test Class for Cli Tests
    """

    runner = CliRunner()
    cli = cli

    def run_query(
        self, base_command: str, args: list[str], response: JSONDict
    ) -> tuple[Result, JSONDict]:
        executor, adapter = get_executor_adapter()
        adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json=response,
        )

        with patch("stacklet.client.platform.executor.requests.Session", autospec=True) as patched:
            with patch("stacklet.client.platform.executor.get_token", return_value="foo"):
                patched.return_value = executor.session
                cli_args = [
                    base_command,
                    "--api=mock://stacklet.acme.org/api",
                    "--cognito-region=us-east-1",
                    "--cognito-user-pool-id=foo",
                    "--cognito-client-id=bar",
                ] + args

                res = self.runner.invoke(self.cli, cli_args)  # type: ignore
                assert res.exit_code == 0, res.stderr
                return res, json.loads(adapter.last_request.body.decode("utf-8"))  # type: ignore
