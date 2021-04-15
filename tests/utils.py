from unittest import TestCase
from unittest.mock import MagicMock

import requests_mock
from click.testing import CliRunner

from cli.cli import cli
from cli.context import StackletContext
from cli.executor import StackletGraphqlExecutor


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
