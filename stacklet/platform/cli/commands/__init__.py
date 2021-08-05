from stacklet.platform.cli.commands.account import account
from stacklet.platform.cli.commands.accountgroup import account_group
from stacklet.platform.cli.commands.binding import binding
from stacklet.platform.cli.commands.graphql import graphql
from stacklet.platform.cli.commands.policy import policy
from stacklet.platform.cli.commands.policycollection import policy_collection
from stacklet.platform.cli.commands.repository import repository
from stacklet.platform.cli.commands.user import user

commands = [
    account,
    account_group,
    binding,
    graphql,
    policy,
    policy_collection,
    repository,
    user,
]
