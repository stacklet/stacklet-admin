

class PluginRegistry:

    def __init__(self, plugin_type):
        self.plugin_type = plugin_type
        self._factories = {}
        self.get = self._factories.get
        self.items = self._factories.items
        self.keys = self._factories.keys
        
    def register(self, name):
        # invoked as class decorator
        def _register_class(klass):
            self._factories[name] = klass
            klass.type = name
            return klass
        return _register_class        
