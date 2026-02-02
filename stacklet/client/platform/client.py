# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

# Stacklet Platform API client based on the CLI

from functools import cached_property
from itertools import chain
from typing import Any

import jmespath

# import the commands so the registry is populated when the client is instantiated
from . import (
    commands,  # noqa
    config,
)
from .config import JSONDict
from .context import StackletContext
from .exceptions import MissingConfigException
from .graphql import GRAPHQL_SNIPPETS, StackletGraphqlExecutor, StackletGraphqlSnippet
from .utils import PAGINATION_OPTIONS


class PlatformApiError(Exception):
    pass


class PlatformTokenExpired(PlatformApiError):
    pass


class StackletPlatformClient:
    """Client to the Stacklet Platform API."""

    def __init__(self, executor: StackletGraphqlExecutor, pager: bool = False, expr: bool = False):
        for name, snippet in GRAPHQL_SNIPPETS.items():
            method = _SnippetMethod(snippet, executor, pager, expr)
            setattr(self, method.name, method)


def platform_client(pager: bool = False, expr: bool = False) -> StackletPlatformClient:
    """
    Return a client for the Stacklet Platform API.

    The client dynamically creates methods from registered GraphQL snippets.
    Each method corresponds to a GraphQL operation available in the platform.

    Args:
        pager: Enable automatic pagination handling. When True, methods that
            support pagination will automatically fetch all pages and return
            the complete result set. Default: False
        expr: Enable result transformation using JMESPath expressions. When True,
            methods will extract and return simplified data structures instead of
            raw GraphQL responses. Default: False

    Returns:
        StackletPlatformClient: A configured client instance with methods for
            each registered GraphQL snippet

    Example:
        >>> client = platform_client()
        >>> accounts = client.list_accounts()
        >>> # With simplified results
        >>> client = platform_client(expr=True)
        >>> accounts = client.list_accounts()  # Returns list of account nodes
        >>> # With automatic pagination
        >>> client = platform_client(pager=True)
        >>> all_accounts = client.list_accounts()  # Fetches all pages
    """
    context = StackletContext(config_file=config.DEFAULT_CONFIG_FILE)
    if not context.config_file.exists() or not context.credentials.api_token():
        raise MissingConfigException("Please configure and authenticate on stacklet-admin cli")

    return StackletPlatformClient(context.executor, pager=pager, expr=expr)


class _SnippetMethod:
    _page_exprs = {
        "list_accounts": "data.accounts.pageInfo",
        "list_policies": "data.policies.pageInfo",
    }

    _result_exprs = {
        "list_account_groups": "data.accountGroups.edges[].node",
        "list_accounts": "data.accounts.edges[].node",
        "list_bindings": "data.bindings.edges[].node",
        "list_repository": "data.repositories.edges[].node",
        "list_policies": "data.policies.edges[].node",
        "list_policy_collections": "data.policyCollections.edges[].node",
        "add_account": "data.addAccount.account",
        "add_account_group": "data.addAccountGroup.group",
        "add_policy_collection": "data.addPolicyCollection.collection",
        "add_repository": "data.addRepository.repository",
        "remove_repository": "data.removeRepository.repository",
        "show_policy_collection": "data.policyCollection",
    }

    def __init__(
        self,
        snippet: StackletGraphqlSnippet,
        executor: StackletGraphqlExecutor,
        pager: bool,
        expr: bool,
    ):
        self.name = snippet.name.replace("-", "_")
        self.snippet = snippet
        self.executor = executor
        self._page_expr = self._page_exprs.get(self.name) if pager else None
        self._result_expr = self._result_exprs.get(self.name) if expr else None

        self.__name__ = self.name
        self.__doc__ = self._doc()

    def __call__(self, **kwargs):
        """Call the snippet."""
        params = self._defaults | kwargs
        page_info, result = self._run_snippet(params)

        # no pagination, just return the reuslt
        if not page_info:
            return result

        # pagination enabled, collect all pages
        pages = [result]

        while page_info["hasNextPage"]:
            params["after"] = page_info["endCursor"]
            page_info, result = self._run_snippet(params)
            pages.append(result)

        # if expr is enabled, flatten the results in a single list
        if self._result_expr:
            return list(chain(*pages))

        return pages

    @cached_property
    def _defaults(self) -> dict[str, Any]:
        """Default parameters."""
        defaults = {}
        if self.snippet.pagination:
            for option, details in PAGINATION_OPTIONS.items():
                defaults[option] = details["default"]
        for option in self.snippet.optional:
            defaults[option] = None

        return defaults

    def _run_snippet(self, params: JSONDict) -> tuple[JSONDict | None, JSONDict]:
        """
        Run the snippet, returning the pagination info (if available) and
        possibly filtered result.
        """
        result = self.executor.run_snippet(self.snippet, variables=params)
        if result == {"message": "The incoming token has expired"}:
            # would be nicer off the 401 status code
            raise PlatformTokenExpired()
        if result.get("errors"):
            raise PlatformApiError(result["errors"])

        page_info = None
        if self._page_expr:
            page_info = jmespath.search(self._page_expr, result)

        if self._result_expr:
            result = jmespath.search(self._result_expr, result)

        return page_info, result

    def _doc(self) -> str:
        lines = []
        if self.snippet.required:
            lines.append("Required parameters: ")
            for param, desc in self.snippet.required.items():
                lines.append(f" {param}: {desc}")
            lines.append("")
        if self.snippet.optional:
            lines.append("Optional parameters: ")
            for param, desc in self.snippet.optional.items():
                lines.append(f" {param}: {desc}")
            lines.append("")
        if self.snippet.pagination:
            lines.append("pagination: ")
            for param, details in PAGINATION_OPTIONS.items():
                lines.append(f" - {param}: {details['help']}")
            lines.append("")
        return "\n".join(lines)
