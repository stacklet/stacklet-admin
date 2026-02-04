# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from ..snippet import GraphQLSnippet


class AddRepository(GraphQLSnippet):
    name = "add-repository"
    snippet = """
    mutation {
      addRepository(
        input: {
          url: $url
          name: $name
          description: $description
          sshPassphrase: $ssh_passphrase
          sshPrivateKey: $ssh_private_key
          authUser: $auth_user
          authToken: $auth_token
          branchName: $branch_name
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
    result_expr = "data.addRepository.repository"


class ProcessRepository(GraphQLSnippet):
    name = "process-repository"
    snippet = """
    mutation {
      processRepository(input:{url: $url})
    }
    """
    required = {"url": "Repository URL to process"}


class ListRepository(GraphQLSnippet):
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
    result_expr = "data.repositories.edges[].node"


class RemoveRepository(GraphQLSnippet):
    name = "remove-repository"
    snippet = """
    mutation {
      removeRepository(
          url: $url
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
    result_expr = "data.removeRepository.repository"


class ScanRepository(GraphQLSnippet):
    name = "scan-repository"
    snippet = """
    mutation {
      processRepository(input:{
          url: $url
          startRevSpec: $start_rev_spec
      })
    }
    """
    required = {
        "url": "Policy Repository URL",
    }

    optional = {"start_rev_spec": "Start Rev Spec"}


class ShowRepository(GraphQLSnippet):
    name = "show-repository"
    snippet = """
    query {
      repository(url: $url) {
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
