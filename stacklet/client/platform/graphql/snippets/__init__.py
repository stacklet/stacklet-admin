# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

from .account import (
    AddAccount,
    ListAccounts,
    RemoveAccount,
    ShowAccount,
    UpdateAccount,
    ValidateAccount,
)
from .account_group import (
    AddAccountGroup,
    AddAccountGroupItem,
    ListAccountGroups,
    RemoveAccountGroup,
    RemoveAccountGroupItem,
    ShowAccountGroup,
    UpdateAccountGroup,
)
from .binding import (
    AddBinding,
    DeployBinding,
    ListBindings,
    RemoveBinding,
    RunBinding,
    ShowBinding,
    UpdateBinding,
)
from .policy import (
    ListPolicies,
    ShowPolicy,
)
from .policy_collection import (
    AddPolicyCollection,
    AddPolicyCollectionItem,
    ListPolicyCollections,
    RemovePolicyCollection,
    RemovePolicyCollectionItem,
    ShowPolicyCollection,
    UpdatePolicyCollection,
)
from .repository import (
    AddRepository,
    ListRepository,
    ProcessRepository,
    RemoveRepository,
    ScanRepository,
    ShowRepository,
)

GRAPHQL_SNIPPETS = frozenset(
    (
        # accounts
        AddAccount,
        ListAccounts,
        RemoveAccount,
        ShowAccount,
        UpdateAccount,
        ValidateAccount,
        # account groups
        AddAccountGroup,
        AddAccountGroupItem,
        ListAccountGroups,
        RemoveAccountGroup,
        RemoveAccountGroupItem,
        ShowAccountGroup,
        UpdateAccountGroup,
        # bindings
        AddBinding,
        DeployBinding,
        ListBindings,
        RemoveBinding,
        RunBinding,
        ShowBinding,
        UpdateBinding,
        # policy collections
        AddPolicyCollection,
        AddPolicyCollectionItem,
        ListPolicyCollections,
        RemovePolicyCollection,
        RemovePolicyCollectionItem,
        ShowPolicyCollection,
        UpdatePolicyCollection,
        # policies
        ListPolicies,
        ShowPolicy,
        # repository
        AddRepository,
        ListRepository,
        ProcessRepository,
        RemoveRepository,
        ScanRepository,
        ShowRepository,
    )
)
