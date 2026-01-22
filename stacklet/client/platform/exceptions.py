# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0


class ConfigValidationException(Exception):
    pass


class InvalidInputException(Exception):
    pass


class MissingToken(Exception):
    def __init__(self):
        super().__init__("Authorization token not configured")
