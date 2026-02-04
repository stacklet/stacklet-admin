# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import click


class MissingConfigException(Exception): ...


class ConfigValidationException(click.ClickException): ...


class InvalidInputException(click.ClickException): ...


class MissingToken(click.ClickException):
    def __init__(self):
        super().__init__("Authorization token not configured")
