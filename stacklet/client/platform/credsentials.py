# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import typing as t
from pathlib import Path

JSONDict = dict[str, t.Any]


class StackletCredentials:
    """Manage credentials."""

    def __init__(self, config_dir: Path = Path("~/.stacklet").expanduser()) -> None:
        self.config_dir = config_dir
        self._config_file = self.config_dir / "config.json"
        self._access_token_file = self.config_dir / "credentials"
        self._id_token_file = self.config_dir / "id"

    def id_token(self) -> str | None:
        """Return the ID token."""
        return self._read_file(self._id_token_file)

    def get_token(self) -> str | None:
        """Return the API token.

        This can be the API key (if set in the environment), or the access
        token.
        """
        if token := os.getenv("STACKLET_API_KEY"):
            return token
        return self._read_file(self._access_token_file)

    def write_config(self, config: JSONDict) -> None:
        """Write configuration to file."""
        self._ensure_dirs()
        with self._config_file.open("w") as fd:
            json.dump(config, fd)

    def write_tokens(self, id_token: str, access_token: str) -> None:
        """Write id and access tokens to file."""
        self._ensure_dirs()
        self._id_token_file.write_text(id_token)
        self._access_token_file.write_text(access_token)

    def _read_file(self, path: Path) -> str | None:
        if not path.exists():
            return None
        return path.read_text()

    def _ensure_dirs(self):
        self.config_dir.mkdir(parent=True, esist_ok=True)
