#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import six
import json


if six.PY2:
    from itertools import imap
    from urllib import quote
    from urlparse import urljoin
    from urlparse import urlparse
elif six.PY3:
    imap = map
    from urllib.parse import quote
    from urllib.parse import urljoin
    from urllib.parse import urlparse


def clean_params(params, drop_nones=True, recursive=True):
    """Clean up a dict of API parameters to be sent to the API.
    Some endpoints require boolean options to be represented as integers. By
    default, will remove all keys whose value is None, so that they will not be
    sent to the API endpoint at all.
    """
    cleaned = {}
    for key, value in six.iteritems(params):
        if drop_nones and value is None:
            continue
        if recursive and isinstance(value, dict):
            value = clean_params(value, drop_nones, recursive)
        cleaned[key] = value
    return cleaned


def encode_params(params, **kwargs):
    """Clean and JSON-encode a dict of parameters."""
    cleaned = clean_params(params, **kwargs)
    return json.dumps(cleaned)

