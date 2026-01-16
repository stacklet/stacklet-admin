from typing import Iterator
from unittest.mock import patch

import pytest
import requests_mock

from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.executor import StackletGraphqlExecutor


@pytest.fixture
def sample_config():
    return {
        "cognito_user_pool_id": "foo",
        "cognito_client_id": "bar",
        "region": "us-east-1",
        "api": "mock://stacklet.acme.org/api",
    }


@pytest.fixture
def mock_api_token() -> Iterator[str]:
    token = "mock-token"
    with patch("stacklet.client.platform.config.StackletCredentials.api_token", return_value=token):
        yield token


@pytest.fixture(autouse=True)
def requests_adapter() -> Iterator[requests_mock.Adapter]:
    """Automatically mock all HTTP requests in tests."""
    with requests_mock.Mocker(real_http=False) as adapter:
        yield adapter


@pytest.fixture
def config_file(tmp_path):
    return tmp_path / "config.json"


@pytest.fixture
def context(mock_api_token, sample_config, config_file) -> StackletContext:
    return StackletContext(raw_config=sample_config, config_file=str(config_file))


@pytest.fixture
def executor(context) -> StackletGraphqlExecutor:
    return StackletGraphqlExecutor(context)
