import json
import os
from contextlib import contextmanager
from unittest.mock import patch

import pytest

from stacklet.client.platform.config import StackletConfig, StackletCredentials
from stacklet.client.platform.exceptions import ConfigValidationException


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


class TestStackletConfig:
    @pytest.fixture
    def config(self):
        return {
            "api": "https://api.example.com",
            "cognito_user_pool_id": "pool-123",
            "cognito_client_id": "client-456",
            "region": "us-east-1",
            "idp_id": "idp-789",
            "auth_url": "https://auth.example.com",
            "cubejs": "https://cubejs.example.com",
        }

    def test_validate_valid_present(self, config):
        StackletConfig.validate(config)

    @pytest.mark.parametrize(
        "missing_field",
        [
            "api",
            "cognito_user_pool_id",
            "cognito_client_id",
            "region",
            "cubejs",
        ],
    )
    def test_validate_missing_required_field(self, config, missing_field):
        del config[missing_field]
        with pytest.raises(ConfigValidationException) as err:
            StackletConfig.validate(config)
        assert f"'{missing_field}' is a required property" in str(err.value)

    @pytest.mark.parametrize(
        "missing_field",
        [
            "idp_id",
            "auth_url",
        ],
    )
    def test_validate_valid_empty_fields(self, config, missing_field):
        del config[missing_field]
        # no error is raised
        StackletConfig.validate(config) is None

    def test_from_dict(self, config):
        conf = StackletConfig.from_dict(config)
        assert conf.to_dict() == config

    def test_from_dict_invalid_config(self, config):
        del config["api"]
        with pytest.raises(ConfigValidationException) as err:
            StackletConfig.from_dict(config)
        assert "'api' is a required property" in str(err.value)

    @pytest.mark.parametrize("extra_param", ["idp_id", "auth_url"])
    def test_to_dict_ignore_optional_unset(self, config, extra_param):
        del config[extra_param]
        conf = StackletConfig.from_dict(config)
        assert extra_param not in conf.to_dict()

    def test_from_file_valid_config(self, config, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config))
        stacklet_config = StackletConfig.from_file(config_file)
        assert stacklet_config.api == config["api"]
        assert stacklet_config.cognito_user_pool_id == config["cognito_user_pool_id"]
        assert stacklet_config.cognito_client_id == config["cognito_client_id"]
        assert stacklet_config.region == config["region"]
        assert stacklet_config.idp_id == config["idp_id"]
        assert stacklet_config.auth_url == config["auth_url"]
        assert stacklet_config.cubejs == config["cubejs"]

    def test_from_file_missing_file(self, tmp_path):
        config_file = tmp_path / "nonexistent.json"
        with pytest.raises(ConfigValidationException):
            StackletConfig.from_file(config_file)

    def test_from_file_invalid_config(self, tmp_path):
        config_file = tmp_path / "config.json"
        incomplete_config = {"api": "https://api.example.com"}
        config_file.write_text(json.dumps(incomplete_config))
        with pytest.raises(ConfigValidationException):
            StackletConfig.from_file(config_file)

    def test_to_file(self, config, tmp_path):
        config_file = tmp_path / "output.json"
        stacklet_config = StackletConfig(**config)
        stacklet_config.to_file(config_file)
        assert config_file.exists()

        loaded_config = StackletConfig.from_file(config_file)
        assert loaded_config.api == config["api"]
        assert loaded_config.cognito_user_pool_id == config["cognito_user_pool_id"]
        assert loaded_config.cognito_client_id == config["cognito_client_id"]
        assert loaded_config.region == config["region"]
        assert loaded_config.idp_id == config["idp_id"]
        assert loaded_config.auth_url == config["auth_url"]
        assert loaded_config.cubejs == config["cubejs"]

    def test_to_file_creates_parent_directories(self, config, tmp_path):
        config_file = tmp_path / "nested" / "dir" / "config.json"
        stacklet_config = StackletConfig(**config)
        stacklet_config.to_file(config_file)
        assert config_file.exists()

        loaded_config = StackletConfig.from_file(config_file)
        assert loaded_config.api == config["api"]
