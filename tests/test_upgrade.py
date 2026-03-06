# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from datetime import date
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from scripts.upgrade import upgrade

VERSION_FILE_CONTENT = """\
# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

__version__ = "{version}"
"""


@pytest.fixture
def version_file(tmp_path):
    f = tmp_path / "__init__.py"
    return f


def invoke(version_file, *args):
    runner = CliRunner()
    with patch("scripts.upgrade.VERSION_FILE", str(version_file)):
        return runner.invoke(upgrade, args)


def set_version(version_file, version):
    version_file.write_text(VERSION_FILE_CONTENT.format(version=version))


def read_version(version_file):
    for line in version_file.read_text().splitlines():
        if line.startswith("__version__"):
            return line.split('"')[1]


class TestPatchBump:
    def test_basic(self, version_file):
        set_version(version_file, "2026.03.06")
        result = invoke(version_file)
        assert result.exit_code == 0
        assert read_version(version_file) == "2026.03.07"

    def test_preserves_zero_padding(self, version_file):
        set_version(version_file, "2026.03.06")
        result = invoke(version_file)
        assert result.exit_code == 0
        assert read_version(version_file) == "2026.03.07"

    def test_rolls_over_without_padding_loss(self, version_file):
        set_version(version_file, "2026.03.09")
        result = invoke(version_file)
        assert result.exit_code == 0
        assert read_version(version_file) == "2026.03.10"

    def test_output_message(self, version_file):
        set_version(version_file, "2026.03.06")
        result = invoke(version_file)
        assert "2026.03.06 -> 2026.03.07" in result.output


class TestTodayBump:
    def test_today(self, version_file):
        set_version(version_file, "2026.01.01")
        with patch("scripts.upgrade.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 6)
            result = invoke(version_file, "today")
        assert result.exit_code == 0
        assert read_version(version_file) == "2026.03.06"

    def test_today_not_a_bump(self, version_file):
        set_version(version_file, "2026.03.06")
        with patch("scripts.upgrade.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 6)
            result = invoke(version_file, "today")
        assert result.exit_code == 1
        assert "not greater" in result.output

    def test_today_earlier_date_fails(self, version_file):
        set_version(version_file, "2026.03.06")
        with patch("scripts.upgrade.date") as mock_date:
            mock_date.today.return_value = date(2026, 3, 5)
            result = invoke(version_file, "today")
        assert result.exit_code == 1
        assert "not greater" in result.output


class TestExplicitVersion:
    def test_explicit_version(self, version_file):
        set_version(version_file, "2026.01.01")
        result = invoke(version_file, "2026.03.06")
        assert result.exit_code == 0
        assert read_version(version_file) == "2026.03.06"

    def test_not_a_bump(self, version_file):
        set_version(version_file, "2026.03.06")
        result = invoke(version_file, "2026.03.06")
        assert result.exit_code == 1
        assert "not greater" in result.output

    def test_older_version_fails(self, version_file):
        set_version(version_file, "2026.03.06")
        result = invoke(version_file, "2026.01.01")
        assert result.exit_code == 1
        assert "not greater" in result.output

    def test_invalid_format(self, version_file):
        set_version(version_file, "2026.03.06")
        result = invoke(version_file, "1.2.3")
        assert result.exit_code == 1
        assert "Invalid version" in result.output

    def test_invalid_format_semver_style(self, version_file):
        set_version(version_file, "2026.03.06")
        result = invoke(version_file, "2026.3.6")
        assert result.exit_code == 1
        assert "Invalid version" in result.output
