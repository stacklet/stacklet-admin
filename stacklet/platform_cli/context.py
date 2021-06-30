from stacklet.platform_cli.config import StackletConfig


class StackletContext:
    """
    CLI Execution Context
    """

    DEFAULT_CONFIG = "~/.stacklet/config.json"
    DEFAULT_CREDENTIALS = "~/.stacklet/credentials"
    DEFAULT_OUTPUT = "yaml"

    def __init__(self, config=None, raw_config=None):
        if all(list(raw_config.values())):
            self.config = StackletConfig(**raw_config)
        elif config:
            self.config = StackletConfig.from_file(config)
        else:
            self.config = StackletConfig.from_file(self.DEFAULT_CONFIG)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return
