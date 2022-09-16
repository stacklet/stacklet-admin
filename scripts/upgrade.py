import sys

import boto3
import click

# in python 3.11 we should switch out to tomllib
import toml
import semver


CODEARTIFACT_DOMAIN = "stacklet"
CODEARTIFACT_DOMAIN_OWNER = "653993915282"  # customer-delivery
CODEARTIFACT_REPOSITORY = "stacklet.client.platform"
CODEARTIFACT_FORMAT = "pypi"
CODEARTIFACT_PACKAGE = "stacklet-client-platform"


@click.group()
def cli():
    """
    c7n-next upgrade tools
    """


@cli.command()
def check_publish():
    client = boto3.client("codeartifact")
    with open("pyproject.toml") as f:
        pyproject = toml.load(f)

    current = pyproject["tool"]["poetry"]["version"]
    current_parsed = semver.VersionInfo.parse(current)

    kwargs = {
        "domain": CODEARTIFACT_DOMAIN,
        "domainOwner": CODEARTIFACT_DOMAIN_OWNER,
        "repository": CODEARTIFACT_REPOSITORY,
        "format": CODEARTIFACT_FORMAT,
        "package": CODEARTIFACT_PACKAGE,
    }

    try:
        package_versions = client.list_package_versions(**kwargs)
        versions = [v["version"] for v in package_versions["versions"]]
    except client.exceptions.ResourceNotFoundException:
        versions = []

    # if our current version is already published we skip and exit 1
    if current_parsed in versions:
        click.echo(
            f"{CODEARTIFACT_PACKAGE}=={current_parsed} already in codeartifact repo, skipping"
        )
        sys.exit(1)
    else:
        click.echo(
            f"{CODEARTIFACT_PACKAGE}=={current_parsed} not in remote codeartifact repo,"
            " OK to publish"
        )
        sys.exit(0)


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

    current = pyproject["tool"]["poetry"]["version"]
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
    click.echo(f"c7n-next: {current_parsed} -> {upgraded}")
    pyproject["tool"]["poetry"]["version"] = upgraded

    with open("pyproject.toml", "w+") as f:
        toml.dump(pyproject, f)


if __name__ == "__main__":
    cli()
