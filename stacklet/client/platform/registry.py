# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0


class PluginRegistry(dict):
    def register(self, name):
        # invoked as class decorator
        def _register_class(klass):
            self[name] = klass
            klass.type = name
            return klass

        return _register_class
