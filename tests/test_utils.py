import os
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import patch

from cli.utils import get_log_level, get_token


class TestUtils(TestCase):
    def setUp(self):
        self.credential_file = NamedTemporaryFile(mode="w+", delete=False)
        with open(self.credential_file.name, "w+") as f:
            f.write("foo")

    def tearDown(self):
        os.unlink(self.credential_file.name)

    @patch("cli.utils.StackletContext")
    def test_get_token(self, patched_context):
        patched_context.DEFAULT_CREDENTIALS = self.credential_file.name
        token = get_token()
        self.assertEqual(token, "foo")

    def test_get_log_level(self):
        self.assertEqual(get_log_level(1), 40)
        self.assertEqual(get_log_level(2), 30)
        self.assertEqual(get_log_level(3), 20)
        self.assertEqual(get_log_level(4), 10)
        self.assertEqual(get_log_level(5), 0)
        self.assertEqual(get_log_level(6), 0)
        self.assertEqual(get_log_level(9999), 0)
