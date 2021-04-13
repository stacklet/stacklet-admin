"""
Handle configuration for the CLI
"""
import json
import os

from jsonschema import ValidationError, validate

from cli.exceptions import ConfigValidationException


class StackletConfig:

    schema = {
        "type": "object",
        "properties": {
            "api": {"type": "string"},
            "cognito_user_pool_id": {"type": "string"},
            "cognito_client_id": {"type": "string"},
            "region": {"type": "string"},
            "username": {"type": "string"},
        },
    }

    def __init__(
        self,
        api=None,
        cognito_user_pool_id=None,
        cognito_client_id=None,
        region=None,
        username=None,
    ):
        self.api = api
        self.cognito_user_pool_id = cognito_user_pool_id
        self.cognito_client_id = cognito_client_id
        self.region = region
        self.username = username

        if not all(
            [self.api, self.cognito_user_pool_id, self.cognito_client_id, self.region]
        ):
            try:
                self = self.from_file(
                    os.path.expanduser("~/.stacklet/config.json")
                )  # noqa
            except ValidationError:
                raise ConfigValidationException

    def to_json(self):
        return dict(
            api=self.api,
            cognito_user_pool_id=self.cognito_user_pool_id,
            cognito_client_id=self.cognito_client_id,
            region=self.region,
        )

    @classmethod
    def validate(cls, instance):
        validate(instance=instance, schema=cls.schema)

    @classmethod
    def from_file(cls, filename):
        with open(os.path.expanduser(filename), "r") as f:
            res = json.load(f)
        cls.validate(res)
        return cls(**res)
