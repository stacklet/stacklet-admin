# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import sys

import click
import semver

# in python 3.11 we should switch out to tomllib
import toml


@click.group()
def cli():
    """
    stacklet-admin upgrade tools
    """


@cli.command()
@click.option("--bump-patch", is_flag=True, default=False)
@click.option("--bump-minor", is_flag=True, default=False)
@click.option("--bump-major", is_flag=True, default=False)
def upgrade(bump_patch, bump_minor, bump_major):
    if sum([bump_patch, bump_minor, bump_major]) != 1:
        click.echo("Only one of --bump-patch/mintor/major may be selected")
        sys.exit(1)

    with open("pyproject.toml") as f:
        pyproject = toml.load(f)

    current = pyproject["project"]["version"]
    current_parsed = semver.VersionInfo.parse(current)

    major = current_parsed.major
    minor = current_parsed.minor
    patch = current_parsed.patch

    if bump_patch:
        patch += 1
    elif bump_minor:
        minor += 1
    elif bump_major:
        major += 1

    upgraded = ".".join([str(x) for x in (major, minor, patch)])
    click.echo(f"stacklet-admin: {current_parsed} -> {upgraded}")
    pyproject["project"]["version"] = upgraded

    with open("pyproject.toml", "w+") as f:
        toml.dump(pyproject, f)


if __name__ == "__main__":
    cli()
