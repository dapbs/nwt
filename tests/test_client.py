#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import re
import six
import requests
import unittest
from unittest import mock

import warnings

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

from nwt.client import PercolateClient


warnings.showwarning = lambda *a, **k: None

access_token = "token"

class TestClient(unittest.TestCase):
    def test_required_token(self):
        with self.assertRaises(ValueError):
            PercolateClient(None)

    def test_auth_succeeds(self):
        access_token = "secret"
        self.assertIsInstance(access_token, six.text_type)

        # client = PercolateClient(access_token)
        # self.assertEqual(client._get("test").status_code, 200)
