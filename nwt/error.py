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


class NotFoundError(APIError):
    pass


class InvalidRequestError(APIError):
    pass


_error_id_to_class = {
    "invalid_request": InvalidRequestError,
    "not_found": NotFoundError,
}

_status_code_to_class = {
    400: InvalidRequestError, 
    404: NotFoundError
}


def build_api_error(response, blob=None):
    """Helper method for creating errors and attaching HTTP response/request
    details to them.
    """
    blob = blob or response.json()
    error_list = blob.get("errors", None)
    error = error_list[0] if error_list else {}
    if error:
        error_id = error.get("id", "")
        error_message = error.get("message", "")
    else:
        error_id = blob.get("error")
        error_message = blob.get("error_description")
    error_class = _error_id_to_class.get(error_id, None) or _status_code_to_class.get(
        response.status_code, APIError
    )
    return error_class(response, error_id, error_message, error_list)

