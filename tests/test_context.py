import json

from stacklet.client.platform.context import StackletContext


class TestStackletContext:
    def test_config(self, config_file, sample_config):
        config_file.write_text(json.dumps(sample_config))
        context = StackletContext(config_file=config_file)
        assert context.config.to_dict() == sample_config
