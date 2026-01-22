import json
from pathlib import Path
from typing import Iterator
from unittest.mock import patch

import pytest
import requests_mock
from click.testing import CliRunner, Result

from stacklet.client.platform.cli import cli
from stacklet.client.platform.config import JSONDict


@pytest.fixture(autouse=True)
def requests_adapter() -> Iterator[requests_mock.Adapter]:
    """Automatically mock all HTTP requests in tests."""
    with requests_mock.Mocker(real_http=False) as adapter:
        yield adapter


@pytest.fixture
def mock_api_token() -> Iterator[str]:
    token = "mock-token"
    with patch(
        "stacklet.client.platform.config.StackletCredentials.api_token",
        return_value=token,
    ):
        yield token


@pytest.fixture
def config_file(tmp_path) -> Path:
    """Path for a configuration file. The file doesn't exist by default."""
    return tmp_path / "config.json"


@pytest.fixture
def sample_config() -> dict[str, str]:
    return {
        "cognito_user_pool_id": "foo",
        "cognito_client_id": "bar",
        "region": "us-east-1",
        "api": "mock://stacklet.acme.org/api",
        "cubejs": "mock://cubejs.stacklet.acme.org",
    }


@pytest.fixture
def sample_config_file(sample_config, config_file) -> Path:
    """Path to a configuration file with a sample config."""
    config_file.write_text(json.dumps(sample_config))
    return config_file


@pytest.fixture
def invoke_cli(config_file):
    """Return a function for invoking the CLI with a sample configuration."""

    def invoke(*cmdargs: str, with_config=True) -> Result:
        args = []
        if with_config:
            args.append(f"--config={config_file}")
        args.extend(cmdargs)
        return CliRunner().invoke(cli, args)

    return invoke


@pytest.fixture
def run_query(requests_adapter, sample_config_file, mock_api_token, invoke_cli):
    def run(base_command: str, args: list[str], response: JSONDict) -> tuple[Result, JSONDict]:
        requests_adapter.register_uri(
            "POST",
            "mock://stacklet.acme.org/api",
            json=response,
        )

        res = invoke_cli(base_command, *args)
        assert res.exit_code == 0, "\n".join(
            [
                f"stderr: {res.stderr}",
                f"stdout: {res.output}",
                f"exception: {res.exception}",
            ]
        )

        payload = json.loads(requests_adapter.last_request.body.decode())
        return res, payload

    return run
