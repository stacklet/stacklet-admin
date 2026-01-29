# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0


class PluginRegistry(dict):
    def __init__(self, plugin_type):
        self.plugin_type = plugin_type

    def register(self, name):
        # invoked as class decorator
        def _register_class(klass):
            self[name] = klass
            klass.type = name
            return klass

        return _register_class
