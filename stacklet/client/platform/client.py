# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

# platform client using cli


import jmespath

# import the commands so the registry is populated when the client is instantiated
from . import (
    commands,  # noqa
    config,
)
from .context import StackletContext
from .exceptions import MissingConfigException
from .graphql import GRAPHQL_SNIPPETS
from .utils import PAGINATION_OPTIONS


def platform_client(pager=False, expr=False):
    # for more pythonic experience, pass expr=True to de-graphqlize the result
    # for automatic pagination handling, pass pager=True
    context = StackletContext(config_file=config.DEFAULT_CONFIG_FILE)
    if not context.config_file.exists() or not context.credentials.api_token():
        raise MissingConfigException("Please configure and authenticate on stacklet-admin cli")

    d = {}

    executor = context.executor

    for k, snippet in GRAPHQL_SNIPPETS.items():
        method_name = k.replace("-", "_")
        d[method_name] = _method(executor, method_name, snippet, pager, expr)

    client_class = type("StackletPlatform", (), d)
    return client_class()


class PlatformApiError(Exception):
    pass


class PlatformTokenExpired(PlatformApiError):
    pass


# todo move these to snippets
result_exprs = {
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

page_exprs = {
    "list_accounts": "data.accounts.pageInfo",
    "list_policies": "data.policies.pageInfo",
}


def _method(executor, function_name, snippet, pager, expr):
    doc = []
    if snippet.required:
        doc.append("required: ")
        for r in snippet.required:
            doc.append(f" - {r}")
        doc.append("")
    if snippet.optional:
        doc.append("optional: ")
        for o in snippet.optional:
            doc.append(f" - {o}")
        doc.append("")
    if snippet.pagination:
        doc.append("pagination: ")
        for p in PAGINATION_OPTIONS:
            doc.append(f" - {p}")
        doc.append("")
    doc = "\n".join(doc)

    defaults = {}
    if snippet.pagination:
        for k, v in PAGINATION_OPTIONS.items():
            defaults[k] = v["default"]
    for k, v in snippet.optional.items():
        defaults[k] = None

    snippet_name = snippet.name

    def api_func(self, **kw):
        params = dict(defaults)
        params.update(kw)

        result = executor.run(snippet_name, variables=params)
        if result == {"message": "The incoming token has expired"}:
            # would be nicer off the 401 status code
            raise PlatformTokenExpired()
        if result.get("errors"):
            raise PlatformApiError(result["errors"])

        if not pager or function_name not in page_exprs:
            if expr and function_name in result_exprs:
                return jmespath.search(result_exprs[function_name], result)
            return result

        pages = [result]
        page_info = jmespath.search(page_exprs[function_name], result)

        while page_info["hasNextPage"]:
            params["after"] = page_info["endCursor"]
            result = executor.run(snippet_name, variables=params)
            if result.get("errors"):
                raise PlatformApiError(result["errors"])
            pages.append(result)
            page_info = jmespath.search(page_exprs[function_name], result)

        if expr and function_name in result_exprs:
            result = []
            for p in pages:
                result.extend(jmespath.search(result_exprs[function_name], p))
        else:
            result = pages
        return result

    api_func.__name__ = function_name
    api_func.__doc__ = doc
    return api_func
