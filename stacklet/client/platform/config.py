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


class StackletConfig:
    schema = {
        "type": "object",
        "properties": {
            "api": {"type": "string"},
            "cognito_user_pool_id": {"type": "string"},
            "cognito_client_id": {"type": "string"},
            "region": {"type": "string"},
            "idp_id": {"type": "string"},
            "auth_url": {"type": "string"},
            "cubejs": {"type": "string"},
        },
    }

    def __init__(
        self,
        api=None,
        cognito_user_pool_id=None,
        cognito_client_id=None,
        region=None,
        idp_id=None,
        auth_url=None,
        cubejs=None,
    ):
        self.api = api
        self.cognito_user_pool_id = cognito_user_pool_id
        self.cognito_client_id = cognito_client_id
        self.region = region
        self.idp_id = idp_id
        self.auth_url = auth_url
        self.cubejs = cubejs

    def to_json(self):
        return dict(
            api=self.api,
            cognito_user_pool_id=self.cognito_user_pool_id,
            cognito_client_id=self.cognito_client_id,
            region=self.region,
            idp_id=self.idp_id,
            auth_url=self.auth_url,
            cubejs=self.cubejs,
        )

    @classmethod
    def validate(cls, config):
        try:
            validate(instance=config, schema=cls.schema)
        except ValidationError as err:
            raise ConfigValidationException(str(err))

    @classmethod
    def from_file(cls, filename):
        path = Path(filename).expanduser()
        if path.exists():
            with path.open() as f:
                content = json.load(f)
        else:
            content = {}

        cls.validate(content)
        return cls(**content)


JSONDict = dict[str, t.Any]


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
