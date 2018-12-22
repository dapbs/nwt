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

from nwt.error import build_api_error

from nwt.models import new_api_object, APIObject, Campaigns


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

        self.session = self._build_session(self.api_key)

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

    def _request(self, method, *relative_path_parts, **kwargs):
        """Internal helper for creating HTTP requests to the Percolate API.
        Raises an APIError if the response is not 20X. Otherwise, returns the
        response object. Not intended for direct use by API consumers.
        """
        uri = self._create_api_uri(*relative_path_parts)
        data = kwargs.get("data", None)
        if data and isinstance(data, dict):
            kwargs["data"] = encode_params(data)
        response = getattr(self.session, method)(uri, **kwargs)
        return self._handle_response(response)

    def _handle_response(self, response):
        """Internal helper for handling API responses from the Percolate.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.
        """
        if not str(response.status_code).startswith("2"):
            raise build_api_error(response)
        return response

    def _get(self, *args, **kwargs):
        """ Get requests can be paginated, ensure we iterate through all the pages """
        prev_data = kwargs.pop("prev_data", [])
        resp = self._request("get", *args, **kwargs)
        resp_content = resp._content
        if not resp_content:
            return resp

        if isinstance(resp_content, bytes):
            resp_content = resp_content.decode("utf-8")

        content = json.loads(resp_content)
        if "pagination" not in content:
            return resp

        page_info = content["pagination"]
        if not page_info["next_uri"]:
            content["data"].extend(prev_data)
            if isinstance(resp_content, bytes):
                resp._content = json.dumps(content).decode("utf-8")
            else:
                resp._content = json.dumps(content)
            return resp

        prev_data.extend(content["data"])
        kwargs.update({"prev_data": prev_data})
        next_page_id = page_info["next_uri"].split("=")[-1]
        kwargs.update({"params": {"starting_after": next_page_id}})
        return self._get(*args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._request("post", *args, **kwargs)

    def _put(self, *args, **kwargs):
        return self._request("put", *args, **kwargs)

    def _delete(self, *args, **kwargs):
        return self._request("delete", *args, **kwargs)

    def _make_api_object(self, response, model_type=None):
        blob = response.json()
        data = blob.get("data", None)
        if data is None:
            raise build_api_error(response, blob)
        warnings_data = blob.get("warnings", None)
        for warning_blob in warnings_data or []:
            message = "%s (%s)" % (
                warning_blob.get("message", ""),
                warning_blob.get("url", ""),
            )
            warnings.warn(message, UserWarning)

        pagination = blob.get("pagination", None)
        kwargs = {
            "response": response,
            "pagination": pagination and new_api_object(None, pagination, APIObject),
            "warnings": warnings_data
            and new_api_object(None, warnings_data, APIObject),
        }
        if isinstance(data, dict):
            obj = new_api_object(self, data, model_type, **kwargs)
        else:
            obj = APIObject(self, **kwargs)
            obj.data = new_api_object(self, data, model_type)
        return obj

    def list_campaings(self, license_ids, **params):
        response = self._get(self.API_VERSION, "campaigns", params=params)
        return self._make_api_object(response, Campaigns)
