# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any

import click

from ..context import StackletContext
from ..exceptions import InvalidInputException
from ..graphql.cli import GraphQLCommand, register_graphql_commands, run_graphql
from ..graphql.snippets import (
    AddPolicyCollection,
    AddRepository,
    ListRepository,
    ProcessRepository,
    RemoveRepository,
    ScanRepository,
    ShowRepository,
)
from ..graphql.snippets.policy_collection import VIEW_OPTIONS
from ..utils import wrap_command


@click.group(short_help="Run repository queries/mutations")
def repository(*args, **kwargs):
    """Query against and Run mutations against Repository objects in Stacklet"""


def _read_ssh_private_key(cli_args: dict[str, Any]) -> None:
    """Replace a --ssh-private-key path with the key itself, in place."""
    private_key = cli_args.get("ssh_private_key")
    if not private_key:
        return
    if cli_args.get("auth_user") is None:
        raise InvalidInputException("Both --auth-user and --ssh-private-key are required")
    with open(os.path.expanduser(private_key), "r") as f:
        cli_args["ssh_private_key"] = f.read().strip("\n")


def _add_pre_check(context: StackletContext, cli_args: dict[str, Any]) -> dict[str, Any]:
    _read_ssh_private_key(cli_args)
    return cli_args


# `register`'s arguments that belong to the repository config half.
REGISTER_REPOSITORY_ARGS = ("url", "name", *AddRepository.optional)

REGISTER_REQUIRED = {
    "url": AddRepository.required["url"],
    "name": AddRepository.required["name"],
    "provider": "Cloud provider for the policy collection",
}

REGISTER_OPTIONAL = {
    **AddRepository.optional,
    "collection_name": "Name for the policy collection. Defaults to the repository name",
    "collection_description": "Policy Collection Description",
    **VIEW_OPTIONS,
    "start_rev_spec": (
        "Revision the first scan starts from. TAIL scans the whole history, recording a "
        "policy version per change -- a deep import. Only settable at creation time, so "
        "it has to be decided here"
    ),
    "deep_import": {
        "help": "Scan the repository's whole history. Shorthand for --start-rev-spec=TAIL",
        "is_flag": True,
    },
}


def register(context: StackletContext, **cli_args):
    """
    Register a policy repository and the dynamic policy collection that scans it.

    Registering a repository takes two mutations. `addRepositoryConfig` records the
    repository's details but gives it no view, and policies are scanned per view -- so a
    bare repository config yields no policies at all. Creating a dynamic policy
    collection is what creates the view and triggers the first scan. This runs both, the
    way the console onboards a repository.

    Use `repository add` and `policy-collection add` to drive either half on its own.
    """
    if cli_args.pop("deep_import"):
        if cli_args["start_rev_spec"]:
            raise InvalidInputException("--deep-import and --start-rev-spec are exclusive")
        cli_args["start_rev_spec"] = "TAIL"

    _read_ssh_private_key(cli_args)

    repo_args = {name: cli_args.pop(name) for name in REGISTER_REPOSITORY_ARGS}
    repo_result = run_graphql(context, snippet_class=AddRepository, variables=repo_args, raw=True)

    added = (repo_result.get("data") or {}).get("addRepositoryConfig") or {}
    if problems := added.get("problems"):
        raise InvalidInputException(
            "could not add repository: %s" % "; ".join(p["message"] for p in problems)
        )
    repo_config = added.get("repositoryConfig")
    if not repo_config:
        # Errors rather than problems: show the response instead of guessing at it.
        raise InvalidInputException("could not add repository: %s" % repo_result)

    repo_uuid = repo_config["uuid"]
    collection_args = dict(cli_args)
    collection_args["repository_uuid"] = repo_uuid
    collection_args["name"] = collection_args.pop("collection_name") or repo_args["name"]
    collection_args["description"] = collection_args.pop("collection_description")
    # A dynamic collection is always auto-updating; the platform rejects anything else.
    collection_args["auto_update"] = "true"

    collection_result = run_graphql(
        context, snippet_class=AddPolicyCollection, variables=collection_args, raw=True
    )
    collection = ((collection_result.get("data") or {}).get("addPolicyCollection") or {}).get(
        "collection"
    )
    if not collection:
        # The repository config exists now, and has no view until a dynamic collection
        # gives it one, so spell out the state rather than leaving it to be rediscovered.
        raise InvalidInputException(
            f"repository {repo_uuid} was added, but creating its policy collection "
            "failed, so nothing will be scanned. Either retry with `policy-collection "
            f"add --repository-uuid={repo_uuid}`, or remove the repository with "
            f"`repository remove --uuid={repo_uuid}`. Response: {collection_result}"
        )

    fmt = context.formatter()
    click.echo(fmt({"repositoryConfig": repo_config, "policyCollection": collection}))


register = wrap_command(register, REGISTER_OPTIONAL)
register = wrap_command(register, REGISTER_REQUIRED, required=True)
repository.add_command(
    click.command(
        "register",
        short_help="Register a repository and a dynamic policy collection to scan it",
    )(click.pass_obj(register))
)


register_graphql_commands(
    repository,
    [
        GraphQLCommand("process", ProcessRepository, "Process a Policy Repository in Stacklet"),
        GraphQLCommand("list", ListRepository, "List repositories"),
        GraphQLCommand(
            "add", AddRepository, "Add a Policy repository to Stacklet", pre_check=_add_pre_check
        ),
        GraphQLCommand("remove", RemoveRepository, "Remove a Policy Repository to Stacklet"),
        GraphQLCommand("scan", ScanRepository, "Scan a repository for policies"),
        GraphQLCommand("show", ShowRepository, "Show a repository"),
    ],
)
