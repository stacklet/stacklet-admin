# platform client using cli

import jmespath
from pathlib import Path

from . import commands  # noqa
from .executor import StackletGraphqlExecutor
from .context import StackletContext
from .utils import get_token, _PAGINATION_OPTIONS


def platform_client(pager=False, expr=False):
    # for more pythonic experience, pass expr=True to de-graphqlize the result
    # for automatic pagination handling, pass pager=True
    if (
        not Path(StackletContext.DEFAULT_CONFIG).expanduser().exists()
        or not Path(StackletContext.DEFAULT_CREDENTIALS).expanduser().exists()
    ):
        raise ValueError("Please configure and authenticate on stacklet-admin cli")

    d = {}
    ctx = StackletContext(raw_config={})
    token = get_token()
    executor = StackletGraphqlExecutor(ctx, token)

    for k, snippet in StackletGraphqlExecutor.registry.items():
        # assert k == snippet.name, f"{k} mismatch {snippet.name}"
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
        for p in _PAGINATION_OPTIONS:
            doc.append(f" - {p}")
        doc.append("")
    doc = "\n".join(doc)

    defaults = {}
    if snippet.pagination:
        for k, v in _PAGINATION_OPTIONS.items():
            defaults[k] = v["default"]
    for k, v in snippet.optional.items():
        defaults[k] = None

    def api_func(self, **kw):
        params = dict(defaults)
        params.update(kw)

        result = executor.run(snippet=snippet, variables=params)
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
            result = executor.run(snippet=snippet, variables=params)
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
