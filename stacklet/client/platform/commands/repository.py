# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import os

import click

from stacklet.client.platform.exceptions import InvalidInputException
from stacklet.client.platform.executor import StackletGraphqlExecutor, _run_graphql, snippet_options
from stacklet.client.platform.graphql import StackletGraphqlSnippet
from stacklet.client.platform.utils import default_options


@StackletGraphqlExecutor.registry.register("add-repository")
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


@StackletGraphqlExecutor.registry.register("process-repository")
class ProcessRepositorySnippet(StackletGraphqlSnippet):
    name = "process-repository"
    snippet = """
    mutation {
      processRepository(input:{url: "$url"})
    }
    """
    required = {"url": "Repository URL to process"}


@StackletGraphqlExecutor.registry.register("list-repository")
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


@StackletGraphqlExecutor.registry.register("remove-repository")
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


@StackletGraphqlExecutor.registry.register("scan-repository")
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
@default_options()
def repository(*args, **kwargs):
    """
    Query against and Run mutations against Repository objects in Stacklet

    Define a custom config file with the --config option

    Specify a different output format with the --output option

    Example:

        $ stacklet repository --output json list

    """


@StackletGraphqlExecutor.registry.register("show-repository")
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


@repository.command()
@snippet_options("add-repository")
@click.pass_obj
def add(obj, **kwargs):
    """
    Add a Policy Repository to Stacklet
    """
    private_key = kwargs.get("ssh_private_key")
    auth_user = kwargs.get("auth_user")
    if private_key:
        if auth_user is None:
            raise InvalidInputException("Both --auth-user and --ssh-private-key are required")
        with open(os.path.expanduser(private_key), "r") as f:
            kwargs["ssh_private_key"] = f.read().strip("\n")
    click.echo(_run_graphql(obj, name="add-repository", variables=kwargs))


@repository.command()
@snippet_options("process-repository")
@click.pass_obj
def process(obj, **kwargs):
    """
    Process a Policy Repository in Stacklet
    """
    click.echo(_run_graphql(obj, name="process-repository", variables=kwargs))


@repository.command()
@snippet_options("list-repository")
@click.pass_obj
def list(obj, **kwargs):
    """
    List repositories
    """
    click.echo(_run_graphql(obj, name="list-repository", variables=kwargs))


@repository.command()
@snippet_options("remove-repository")
@click.pass_obj
def remove(obj, **kwargs):
    """
    Remove a Policy Repository to Stacklet
    """
    click.echo(_run_graphql(obj, name="remove-repository", variables=kwargs))


@repository.command()
@snippet_options("scan-repository")
@click.pass_obj
def scan(obj, **kwargs):
    """
    Scan a repository for policies
    """
    click.echo(_run_graphql(obj, name="scan-repository", variables=kwargs))


@repository.command()
@snippet_options("show-repository")
@click.pass_obj
def show(obj, **kwargs):
    """
    Show a repository
    """
    click.echo(_run_graphql(obj, name="show-repository", variables=kwargs))
