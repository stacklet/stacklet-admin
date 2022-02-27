import json

import yaml
from .registry import PluginRegistry


class Formatter:

    registry = PluginRegistry("formats")


@Formatter.registry.register("")
class NullFormatter(Formatter):
    def __call__(self, value):
        raise NotImplementedError("Null Formatter")


@Formatter.registry.register("plain")
class RawFormatter(Formatter):
    def __call__(self, value):
        return str(value)


@Formatter.registry.register("json")
class JsonFormatter(Formatter):
    def __call__(self, value):
        return json.dumps(value, indent=2)


@Formatter.registry.register("yaml")
class YamlFormatter(Formatter):
    def __call__(self, value):
        return yaml.safe_dump(value, indent=2)
