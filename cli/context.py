from cli.config import StackletConfig


class StackletContext:
    """
    CLI Execution Context
    """

    DEFAULT_CONFIG = "~/.stacklet/config.json"
    DEFAULT_CREDENTIALS = "~/.stacklet/credentials"
    DEFAULT_OUTPUT = "yaml"

    def __init__(self, config=None):
        if config is None:
            self.config = StackletConfig.from_file(self.DEFAULT_CONFIG)
        else:
            self.config = StackletConfig.from_file(config)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return
