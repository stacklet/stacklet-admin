# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from ...utils import BOOL_CHOICE, to_bool
from ..snippet import GraphQLSnippet


class AddRepository(GraphQLSnippet):
    name = "add-repository"
    snippet = """
    mutation {
      addRepositoryConfig(
        input: {
          url: $url
          name: $name
          description: $description
          auth: {
            authUser: $auth_user
            authToken: $auth_token
            sshPrivateKey: $ssh_private_key
            sshPassphrase: $ssh_passphrase
          }
          webhookSecret: $webhook_secret
        }
      ) {
        repositoryConfig {
            uuid
            url
            name
        }
        problems {
            message
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
        "webhook_secret": "Secret used to validate repository webhook payloads",
    }
    result_expr = "data.addRepositoryConfig.repositoryConfig"


class ProcessRepository(GraphQLSnippet):
    name = "process-repository"
    snippet = """
    mutation {
      triggerRepositoryScan(input:{uuid: $uuid}) {
        problems {
            message
        }
      }
    }
    """
    required = {"uuid": "Repository Config UUID"}
    result_expr = "data.triggerRepositoryScan"


class ScanRepository(GraphQLSnippet):
    name = "scan-repository"
    snippet = """
    mutation {
      triggerRepositoryScan(input:{uuid: $uuid}) {
        problems {
            message
        }
      }
    }
    """
    required = {"uuid": "Repository Config UUID"}
    result_expr = "data.triggerRepositoryScan"


class ListRepository(GraphQLSnippet):
    name = "list-repository"
    snippet = """
    query {
      repositoryConfigs {
        edges {
          node {
            id
            uuid
            name
            url
            provider
            auth {
                authUser
                sshPublicKey
            }
            globalView {
                branchName
                policyFileSuffix
                policyDirectories
                head
                lastScanned
            }
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
    result_expr = "data.repositoryConfigs.edges[].node"


class RemoveRepository(GraphQLSnippet):
    name = "remove-repository"
    snippet = """
    mutation {
      removeRepositoryConfig(
          input: {
              uuid: $uuid
              cascade: $cascade
          }
      ) {
        removed {
            id
        }
        problems {
            message
        }
      }
    }
    """
    required = {
        "uuid": "Repository Config UUID",
    }
    optional = {
        "cascade": {
            "help": "Also remove bindings and policy collections tied to this repository",
            "default": "false",
            "type": BOOL_CHOICE,
        },
    }
    variable_transformers = {"cascade": to_bool}
    result_expr = "data.removeRepositoryConfig"


class ShowRepository(GraphQLSnippet):
    name = "show-repository"
    snippet = """
    query {
      repositoryConfig(uuid: $uuid) {
        repositoryConfig {
            id
            uuid
            name
            url
            provider
            webhookURL
            hasWebhookSecret
            created
            modified
            auth {
                authUser
                sshPublicKey
                hasAuthToken
                hasSshPrivateKey
                hasSshPassphrase
                connectStatus
                connectError
            }
            globalView {
                uuid
                branchName
                policyFileSuffix
                policyDirectories
                head
                lastScanned
                scans {
                    edges {
                        node {
                            started
                            completed
                            head
                            errors {
                                ... on SimpleScanError {
                                    type
                                    messages
                                }
                                ... on DuplicatePolicyError {
                                    type
                                    policyName
                                    path
                                    otherRepository
                                    otherPath
                                    commitHash
                                }
                                ... on DashboardError {
                                    type
                                    issues {
                                        title
                                        message
                                    }
                                }
                            }
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
        problems {
            message
        }
      }
    }
    """

    required = {"uuid": "Repository Config UUID"}
    result_expr = "data.repositoryConfig.repositoryConfig"
