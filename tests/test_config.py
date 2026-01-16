import os
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from stacklet.client.platform.config import StackletConfigFiles


@pytest.fixture
def files(tmp_path_factory) -> StackletConfigFiles:
    return StackletConfigFiles(tmp_path_factory.mktemp("config"))


class TestStackletConfigFiles:
    @contextmanager
    def env_api_key(self, key):
        with patch.dict(os.environ, {"STACKLET_API_KEY": key}):
            yield

    def test_write_tokens(self, files):
        files.write_tokens("id token", "access token")
        assert (files.config_dir / "id").read_text() == "id token"
        assert (files.config_dir / "credentials").read_text() == "access token"

    def test_read_config_empty(self, files):
        assert files.read_config() is None

    def test_read_write_config(self, files):
        config = {"test": "content"}
        files.write_config(config)
        assert files.read_config() == config

    def test_id_token_missing(self, files):
        assert files.id_token() is None

    def test_id_token(self, files):
        files.write_tokens("id token", "access token")
        assert files.id_token() == "id token"

    def test_api_token_missing(self, files):
        assert files.api_token() is None

    def test_api_token_from_file(self, files):
        files.write_tokens("id token", "access token")
        assert files.api_token() == "access token"

    def test_api_token_from_env(self, files):
        with self.env_api_key("a-b-c"):
            assert files.api_token() == "a-b-c"

    def test_api_token_prefer_env(self, files):
        files.write_tokens("id token", "access token")
        with self.env_api_key("a-b-c"):
            assert files.api_token() == "a-b-c"
