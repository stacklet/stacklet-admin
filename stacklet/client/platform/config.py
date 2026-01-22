# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Handle configuration for the CLI
"""

import json
import os
import typing as t
from pathlib import Path

from jsonschema import ValidationError, validate

from .exceptions import ConfigValidationException

MISSING = "missing"


DEFAULT_CONFIG_DIR = Path("~/.stacklet").expanduser()
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"

DEFAULT_OUTPUT_FORMAT = "yaml"

JSONDict = dict[str, t.Any]


class StackletConfig:
    schema = {
        "type": "object",
        "properties": {
            "api": {"type": "string"},
            "cognito_user_pool_id": {"type": "string"},
            "cognito_client_id": {"type": "string"},
            "region": {"type": "string"},
            "cubejs": {"type": "string"},
            "idp_id": {"type": "string"},
            "auth_url": {"type": "string"},
        },
        "required": [
            "api",
            "cognito_user_pool_id",
            "cognito_client_id",
            "region",
            "cubejs",
        ],
    }

    def __init__(
        self,
        api,
        cognito_user_pool_id,
        cognito_client_id,
        region,
        cubejs,
        idp_id=None,
        auth_url=None,
    ):
        self.api = api
        self.cognito_user_pool_id = cognito_user_pool_id
        self.cognito_client_id = cognito_client_id
        self.region = region
        self.cubejs = cubejs
        self.idp_id = idp_id
        self.auth_url = auth_url

    @classmethod
    def from_dict(cls, config: JSONDict):
        cls.validate(config)
        return cls(**config)

    def to_dict(self) -> JSONDict:
        d = {
            "api": self.api,
            "cognito_user_pool_id": self.cognito_user_pool_id,
            "cognito_client_id": self.cognito_client_id,
            "region": self.region,
            "cubejs": self.cubejs,
        }
        if self.idp_id is not None:
            d["idp_id"] = self.idp_id
        if self.auth_url is not None:
            d["auth_url"] = self.auth_url
        return d

    @classmethod
    def from_file(cls, path: Path):
        path = path.expanduser()
        if not path.exists():
            raise ConfigValidationException(f"Configuration file not found: {path}")
        with path.open() as f:
            config = json.load(f)
        return cls.from_dict(config)

    def to_file(self, path: Path):
        path = path.expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as fd:
            json.dump(self.to_dict(), fd, indent=4, sort_keys=True)

    @classmethod
    def validate(cls, config: JSONDict):
        try:
            return validate(instance=config, schema=cls.schema)
        except ValidationError as err:
            raise ConfigValidationException(str(err))


class StackletCredentials:
    """Manage credentials files."""

    def __init__(self, config_dir: Path = DEFAULT_CONFIG_DIR) -> None:
        self.config_dir = config_dir
        self._access_token_file = self.config_dir / "credentials"
        self._id_token_file = self.config_dir / "id"

    def id_token(self) -> str | None:
        """Return the ID token."""
        return self._read_file(self._id_token_file)

    def api_token(self) -> str | None:
        """Return the API token.

        This can be the API key (if set in the environment), or the access
        token.
        """
        if token := os.getenv("STACKLET_API_KEY"):
            return token
        return self._read_file(self._access_token_file)

    def write(self, id_token: str, access_token: str) -> None:
        """Write id and access tokens to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._id_token_file.write_text(id_token)
        self._access_token_file.write_text(access_token)

    def _read_file(self, path: Path) -> str | None:
        if not path.exists():
            return None
        return path.read_text()
