# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from .account import account
from .accountgroup import account_group
from .binding import binding
from .cube import cubejs
from .graphql import graphql
from .policy import policy
from .policycollection import policy_collection
from .repository import repository
from .user import user

commands = [
    account,
    account_group,
    binding,
    cubejs,
    graphql,
    policy,
    policy_collection,
    repository,
    user,
]
