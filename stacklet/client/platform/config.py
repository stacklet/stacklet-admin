"""
Handle configuration for the CLI
"""
import json
import os

from jsonschema import ValidationError, validate
from stacklet.client.platform.exceptions import ConfigValidationException

MISSING = "missing"


class StackletConfig:

    schema = {
        "type": "object",
        "properties": {
            "api": {"type": "string"},
            "cognito_user_pool_id": {"type": "string"},
            "cognito_client_id": {"type": "string"},
            "region": {"type": "string"},
            "idp_id": {"type": "string"},
            "auth_url": {"type": "string"},
            "cubejs": {"type": "string"},
        },
    }

    def __init__(
        self,
        api=None,
        cognito_user_pool_id=None,
        cognito_client_id=None,
        region=None,
        idp_id=None,
        auth_url=None,
        cubejs=None,
    ):
        self.api = api
        self.cognito_user_pool_id = cognito_user_pool_id
        self.cognito_client_id = cognito_client_id
        self.region = region
        self.idp_id = idp_id
        self.auth_url = auth_url
        self.cubejs = cubejs

        if not all(
            [self.api, self.cognito_user_pool_id, self.cognito_client_id, self.region]
        ):
            try:
                path = "~/.stacklet/config.json"
                if os.environ.get("STACKLET_CONFIG"):
                    path = os.environ["STACKLET_CONFIG"]
                self = self.from_file(os.path.expanduser(path))  # noqa
            except ValidationError:
                raise ConfigValidationException
            raise ConfigValidationException

    def to_json(self):
        return dict(
            api=self.api,
            cognito_user_pool_id=self.cognito_user_pool_id,
            cognito_client_id=self.cognito_client_id,
            region=self.region,
            idp_id=self.idp_id,
            auth_url=self.auth_url,
            cubejs=self.cubejs,
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
