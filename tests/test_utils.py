# Copyright Stacklet, Inc.
# SPDX-License-Identifier: Apache-2.0

import os
from tempfile import NamedTemporaryFile
from unittest import TestCase

from stacklet.client.platform.formatter import (
    JsonFormatter,
    RawFormatter,
    YamlFormatter,
)
from stacklet.client.platform.utils import get_log_level


class UtilsTest(TestCase):
    def setUp(self):
        self.credential_file = NamedTemporaryFile(mode="w+", delete=False)
        with open(self.credential_file.name, "w+") as f:
            f.write("foo")

    def tearDown(self):
        os.unlink(self.credential_file.name)

    def test_get_log_level(self):
        self.assertEqual(get_log_level(-9999), 50)
        self.assertEqual(get_log_level(0), 40)
        self.assertEqual(get_log_level(1), 30)
        self.assertEqual(get_log_level(2), 20)
        self.assertEqual(get_log_level(3), 10)
        self.assertEqual(get_log_level(4), 0)
        self.assertEqual(get_log_level(5), 0)
        self.assertEqual(get_log_level(6), 0)
        self.assertEqual(get_log_level(9999), 0)

    def test_formatters(self):
        input_string = {"foo": "bar"}
        result = RawFormatter()(input_string)
        self.assertEqual(result, "{'foo': 'bar'}")

        result = JsonFormatter()(input_string)
        self.assertEqual(result, '{\n  "foo": "bar"\n}')

        result = YamlFormatter()(input_string)
        self.assertEqual(result, "foo: bar\n")
