# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any
from unittest import TestCase

import pytest
from click.testing import CliRunner, Result

from stacklet.client.platform.cli import cli

JSONDict = dict[str, Any]


class BaseCliTest(TestCase):
    """
    Base Test Class for Cli Tests
    """

    @pytest.fixture(autouse=True)
    def _setup(self, requests_adapter, executor):
        self.runner = CliRunner()
        self.cli = cli
        self.adapter = requests_adapter
        self.executor = executor

    def run_query(
        self, base_command: str, args: list[str], response: JSONDict
    ) -> tuple[Result, JSONDict]:
        self.adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json=response,
        )

        cli_args = [
            "--api=mock://stacklet.acme.org/api",
            "--cognito-region=us-east-1",
            "--cognito-user-pool-id=foo",
            "--cognito-client-id=bar",
            base_command,
        ] + args

        res = self.runner.invoke(self.cli, cli_args)  # type: ignore
        assert res.exit_code == 0, (
            f"stderr: {res.stderr}\nstdout: {res.output}\nexception: {res.exception}"
        )
        return res, json.loads(self.adapter.last_request.body.decode("utf-8"))  # type: ignore
