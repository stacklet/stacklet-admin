# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
from typing import Any

import click

from ..context import StackletContext
from ..exceptions import InvalidInputException
from ..graphql import GRAPHQL_SNIPPETS, StackletGraphqlSnippet
from ..graphql_cli import GraphQLCommand, register_graphql_commands


@GRAPHQL_SNIPPETS.register("add-repository")
class AddRepositorySnippet(StackletGraphqlSnippet):
    name = "add-repository"
    snippet = """
    mutation {
      addRepository(
        input: {
          url: "$url"
          name: "$name"
          description: "$description"
          sshPassphrase: "$ssh_passphrase"
          sshPrivateKey: "$ssh_private_key"
          authUser: "$auth_user"
          authToken: "$auth_token"
          branchName: "$branch_name"
          policyFileSuffix: $policy_file_suffix
          policyDirectories: $policy_directory
          deepImport: $deep_import
        }
      ) {
        repository {
            url
            name
        }
      }
    }
    """
    required = {
        "url": "Policy Repository URL",
        "name": "Human Readable Policy Repository Name",
    }

    optional = {
        "description": "Repo Description",
        "ssh_passphrase": "SSH Passphrase for Private Key",
        "ssh_private_key": "Path to a SSH Private Key",
        "auth_user": "Auth User for repository access",
        "auth_token": "Auth token for repository access",
        "branch_name": "Git Branch Name",
        "policy_file_suffix": {
            "help": 'List of Policy File Suffixes e.g. [".json", ".yaml", ".yml"]',
            "multiple": True,
        },
        "policy_directory": {
            "help": 'Policy Directories e.g. ["policies", "some/path"]',
            "multiple": True,
        },
        "deep_import": "Deep Import Repository true | false",
    }
    variable_transformers = {"deep_import": lambda x: x and x.lower() in ("true", "t", "yes", "y")}


@GRAPHQL_SNIPPETS.register("process-repository")
class ProcessRepositorySnippet(StackletGraphqlSnippet):
    name = "process-repository"
    snippet = """
    mutation {
      processRepository(input:{url: "$url"})
    }
    """
    required = {"url": "Repository URL to process"}


@GRAPHQL_SNIPPETS.register("list-repository")
class ListRepositorySnippet(StackletGraphqlSnippet):
    name = "list-repository"
    snippet = """
    query {
      repositories {
        edges {
          node {
            id
            name
            url
            policyFileSuffix
            policyDirectories
            branchName
            authUser
            sshPublicKey
            head
            lastScanned
            provider
          }
        }
        pageInfo {
          hasPreviousPage
          hasNextPage
          startCursor
          endCursor
          total
        }
      }
    }
    """


@GRAPHQL_SNIPPETS.register("remove-repository")
class RemoveRepositorySnippet(StackletGraphqlSnippet):
    name = "remove-repository"
    snippet = """
    mutation {
      removeRepository(
          url: "$url"
      ) {
        repository {
            url
            name
        }
      }
    }
    """
    required = {
        "url": "Policy Repository URL",
    }


@GRAPHQL_SNIPPETS.register("scan-repository")
class ScanRepositorySnippet(StackletGraphqlSnippet):
    name = "scan-repository"
    snippet = """
    mutation {
      processRepository(input:{
          url: "$url"
          startRevSpec: "$start_rev_spec"
      })
    }
    """
    required = {
        "url": "Policy Repository URL",
    }

    optional = {"start_rev_spec": "Start Rev Spec"}


@click.group(short_help="Run repository queries/mutations")
def repository(*args, **kwargs):
    """Query against and Run mutations against Repository objects in Stacklet"""


@GRAPHQL_SNIPPETS.register("show-repository")
class ShowRepositorySnippet(StackletGraphqlSnippet):
    name = "show-repository"
    snippet = """
    query {
      repository(url: "$url") {
        id
        name
        url
        policyFileSuffix
        policyDirectories
        branchName
        authUser
        sshPublicKey
        head
        lastScanned
        provider
        scans {
          edges {
            node {
              started
              completed
              head
              error
              commitsProcessed
              policiesAdded
              policiesModified
              policiesRemoved
              policiesInvalid
            }
          }
          pageInfo {
            hasPreviousPage
            hasNextPage
            startCursor
            endCursor
            total
          }
        }
      }
    }
    """

    required = {"url": "Repository URL to process"}


def _add_pre_check(context: StackletContext, cli_args: dict[str, Any]) -> dict[str, Any]:
    private_key = cli_args.get("ssh_private_key")
    auth_user = cli_args.get("auth_user")
    if private_key:
        if auth_user is None:
            raise InvalidInputException("Both --auth-user and --ssh-private-key are required")
        with open(os.path.expanduser(private_key), "r") as f:
            cli_args["ssh_private_key"] = f.read().strip("\n")

    return cli_args


register_graphql_commands(
    repository,
    [
        GraphQLCommand("process", "process-repository", "Process a Policy Repository in Stacklet"),
        GraphQLCommand("list", "list-repository", "List repositories"),
        GraphQLCommand(
            "add", "add-repository", "Add a Policy repository to Stacklet", pre_check=_add_pre_check
        ),
        GraphQLCommand("remove", "remove-repository", "Remove a Policy Repository to Stacklet"),
        GraphQLCommand("scan", "scan-repository", "Scan a repository for policies"),
        GraphQLCommand("show", "show-repository", "Show a repository"),
    ],
)
