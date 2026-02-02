# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
import logging

import requests

from ..config import JSONDict
from ..utils import USER_AGENT
from .snippet import AdHocSnippet, GraphQLSnippet


class GraphQLExecutor:
    """Execute Graphql queries against the API."""

    def __init__(self, api: str, token: str):
        self.api = api
        self.token = token
        self.log = logging.getLogger("GraphQLExecutor")

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "User-Agent": USER_AGENT,
            }
        )

    def run_query(self, query: str) -> JSONDict:
        """Run a literal GraphQL query string."""
        snippet = type("AdHocSnippet", (AdHocSnippet,), {"snippet": query})
        return self.run_snippet(snippet)

    def run_snippet(
        self,
        snippet_class: type[GraphQLSnippet],
        variables: JSONDict | None = None,
        transform_variables: bool = False,
    ) -> JSONDict:
        """Run a graphql snippet."""
        if transform_variables:
            variables = snippet_class.transform_variables(variables)
        request = snippet_class.build(variables)
        self.log.debug("Request: %s" % json.dumps(request, indent=2))
        res = self.session.post(self.api, json=request)
        self.log.debug("Response: %s" % json.dumps(res.json(), indent=2))
        return res.json()
