import os
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from stacklet.client.platform.config import StackletCredentials


@pytest.fixture
def creds(tmp_path_factory) -> StackletCredentials:
    return StackletCredentials(tmp_path_factory.mktemp("config"))


class TestStackletCredentials:
    @contextmanager
    def env_api_key(self, key):
        with patch.dict(os.environ, {"STACKLET_API_KEY": key}):
            yield

    def test_write(self, creds):
        creds.write("id token", "access token")
        assert (creds.config_dir / "id").read_text() == "id token"
        assert (creds.config_dir / "credentials").read_text() == "access token"

    def test_id_token_missing(self, creds):
        assert creds.id_token() is None

    def test_id_token(self, creds):
        creds.write("id token", "access token")
        assert creds.id_token() == "id token"

    def test_api_token_missing(self, creds):
        assert creds.api_token() is None

    def test_api_token_from_file(self, creds):
        creds.write("id token", "access token")
        assert creds.api_token() == "access token"

    def test_api_token_from_env(self, creds):
        with self.env_api_key("a-b-c"):
            assert creds.api_token() == "a-b-c"

    def test_api_token_prefer_env(self, creds):
        creds.write("id token", "access token")
        with self.env_api_key("a-b-c"):
            assert creds.api_token() == "a-b-c"
