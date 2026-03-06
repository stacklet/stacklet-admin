# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import re
import sys
from datetime import date

import click

VERSION_FILE = "stacklet/client/platform/__init__.py"
VERSION_RE = re.compile(r'^__version__ = "(.+)"$', re.MULTILINE)


def parse_version(v):
    return tuple(int(x) for x in v.split("."))


@click.command()
@click.argument("version", required=False)
def upgrade(version):
    """Set the package version.

    With no argument, bumps the patch component of the current version.
    Pass 'today' to use today's date (YYYY.MM.DD), or an explicit YYYY.MM.DD.
    The latter two will error if the result is not greater than the current version.
    """
    with open(VERSION_FILE) as f:
        content = f.read()

    match = VERSION_RE.search(content)
    if not match:
        click.echo(f"Could not find __version__ in {VERSION_FILE}")
        sys.exit(1)

    current = match.group(1)

    if version is None:
        parts = current.split(".")
        parts[-1] = str(int(parts[-1]) + 1).zfill(len(parts[-1]))
        new_version = ".".join(parts)
    else:
        if version == "today":
            new_version = date.today().strftime("%Y.%m.%d")
        else:
            new_version = version

        if not re.match(r"^\d{4}\.\d{2}\.\d{2}$", new_version):
            click.echo(f"Invalid version: {new_version!r}. Expected YYYY.MM.DD or 'today'.")
            sys.exit(1)

        if parse_version(new_version) <= parse_version(current):
            click.echo(f"Version {new_version!r} is not greater than current {current!r}.")
            sys.exit(1)

    with open(VERSION_FILE, "w") as f:
        f.write(VERSION_RE.sub(f'__version__ = "{new_version}"', content))

    click.echo(f"{current} -> {new_version}")


if __name__ == "__main__":
    upgrade()
