#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import base64
import json
import os
import requests
import six
import warnings

from nwt.utils import imap
from nwt.utils import quote
from nwt.utils import urljoin
from nwt.utils import encode_params


class PercolateClient(object):
    """ NWT: Unofficial API Client for the Percolate API.
    Entry point for making requests to the Percolate API. Provides helper methods
    for common API endpoints.
    Full API docs, including descriptions of each API and its paramters, are
    available here: https://percolate.com/docs/api/)
    """

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Missing `api_key`.")
        self.api_key = api_key
        self.BASE_API_URI = "https://percolate.com/api/"
        self.API_VERSION = "v5"

    def _build_session(self, *args, **kwargs):
        """Internal helper for creating a requests `session` with the correct
        authentication handling."""
        session = requests.session()
        session.headers.update(
            {
                "Authorization": "Bearer " + self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "nwt/python",
            }
        )
        return session

    def _create_api_uri(self, *parts):
        """Internal helper for creating fully qualified endpoint URIs."""
        return urljoin(self.BASE_API_URI, "/".join(imap(quote, parts)))
