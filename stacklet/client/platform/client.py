# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

# Stacklet Platform API client based on the CLI

from functools import cached_property
from itertools import chain
from typing import Any

import jmespath

from . import config
from .config import JSONDict
from .context import StackletContext
from .exceptions import MissingConfigException
from .graphql import GRAPHQL_SNIPPETS, GraphQLExecutor, GraphQLSnippet
from .utils import PAGINATION_OPTIONS


class PlatformApiError(Exception):
    pass


class PlatformTokenExpired(PlatformApiError):
    pass


class StackletPlatformClient:
    """Client to the Stacklet Platform API."""

    def __init__(self, executor: GraphQLExecutor, pager: bool = False, expr: bool = False):
        for snippet in GRAPHQL_SNIPPETS:
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
    def __init__(
        self,
        snippet_class: type[GraphQLSnippet],
        executor: GraphQLExecutor,
        pager: bool,
        expr: bool,
    ):
        self.name = snippet_class.name.replace("-", "_")
        self.snippet_class = snippet_class
        self.executor = executor
        self._page_expr = snippet_class.pagination_expr if pager else None
        self._result_expr = snippet_class.result_expr if expr else None

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
        if self.snippet_class.pagination_expr is not None:
            for option, details in PAGINATION_OPTIONS.items():
                defaults[option] = details["default"]
        for option in self.snippet_class.optional:
            defaults[option] = None

        return defaults

    def _run_snippet(self, params: JSONDict) -> tuple[JSONDict | None, JSONDict]:
        """
        Run the snippet, returning the pagination info (if available) and
        possibly filtered result.
        """
        result = self.executor.run_snippet(self.snippet_class, variables=params)
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
        if self.snippet_class.required:
            lines.append("Required parameters: ")
            for param, desc in self.snippet_class.required.items():
                lines.append(f" {param}: {desc}")
            lines.append("")
        if self.snippet_class.optional:
            lines.append("Optional parameters: ")
            for param, details in self.snippet_class.optional.items():
                if isinstance(details, str):
                    desc = details
                else:
                    desc = details["help"]
                lines.append(f" {param}: {desc}")
            lines.append("")
        if self.snippet_class.pagination_expr is not None:
            lines.append("pagination: ")
            for param, details in PAGINATION_OPTIONS.items():
                lines.append(f" - {param}: {details['help']}")
            lines.append("")
        return "\n".join(lines)
