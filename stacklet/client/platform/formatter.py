# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import json
from abc import abstractmethod

import yaml


class Formatter:
    @abstractmethod
    def __call__(self, value): ...


class RawFormatter(Formatter):
    def __call__(self, value):
        return str(value)


class JSONFormatter(Formatter):
    def __call__(self, value):
        return json.dumps(value, indent=2)


class YAMLFormatter(Formatter):
    def __call__(self, value):
        return yaml.safe_dump(value, indent=2)


FORMATTERS = {
    "plain": RawFormatter,
    "json": JSONFormatter,
    "yaml": YAMLFormatter,
}
