#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class PercolateError(Exception):
    raise NotImplementedError


class APIError(PercolateError):
    """Raised for errors related to interacting with the Percolate API"""

    def __init__(self, response, id, message, errors=None):
        self.status_code = response.status_code
        self.response = response
        self.id = id or ""
        self.message = message or ""
        self.request = getattr(response, "request", None)
        self.errors = errors or []

    def __str__(self):
        return "APIError(id=%s): %s" % (self.id, self.message)
