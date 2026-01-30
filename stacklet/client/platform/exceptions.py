# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click


class MissingConfigException(click.ClickException): ...


class ConfigValidationException(click.ClickException): ...


class InvalidInputException(click.ClickException): ...


class MissingToken(click.ClickException):
    def __init__(self):
        super().__init__("Authorization token not configured")


class UnknownSnippet(click.ClickException):
    def __init__(self, name: str):
        super().__init__(f"Unknown GraphQL snippet: {name}")
