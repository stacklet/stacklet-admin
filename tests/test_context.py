import json

import pytest

from stacklet.client.platform.context import StackletContext
from stacklet.client.platform.exceptions import MissingToken
from stacklet.client.platform.graphql import GraphQLExecutor


class TestStackletContext:
    def test_config(self, config_file, sample_config):
        config_file.write_text(json.dumps(sample_config))
        context = StackletContext(config_file=config_file)
        assert context.config.to_dict() == sample_config

    def test_executor(self, config_file, sample_config, api_token_in_file):
        config_file.write_text(json.dumps(sample_config))
        context = StackletContext(config_file=config_file)
        executor = context.executor
        assert isinstance(executor, GraphQLExecutor)
        assert executor.api == "mock://stacklet.acme.org/api"
        assert executor.token == api_token_in_file

    def test_executor_missing_token(self, config_file, sample_config):
        config_file.write_text(json.dumps(sample_config))
        context = StackletContext(config_file=config_file)
        with pytest.raises(MissingToken):
            _ = context.executor
