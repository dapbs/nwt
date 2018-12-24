#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import six


class APIObject(dict):
    """Generic class used to represent a JSON response from the Percolate API.
    If you're a consumer of the API, you shouldn't be using this class directly.
    This exists to make it easier to consume our API by allowing dot-notation
    access to the responses, as well as automatically parsing the responses into
    the appropriate Python models.
    """

    __api_client = None
    __response = None
    __pagination = None
    __warnings = None

    def __init__(self, api_client, response=None, pagination=None, warnings=None):
        self.__api_client = api_client
        self.__response = response
        self.__pagination = pagination
        self.__warnings = warnings

    @property
    def api_client(self):
        return self.__api_client

    @property
    def response(self):
        return self.__response

    @property
    def warnings(self):
        return self.__warnings

    @property
    def pagination(self):
        return self.__pagination

    def refresh(self, **params):
        url = getattr(self, "resource_path", None)
        if not url:
            raise ValueError("Unable to refresh: missing 'resource_path' attribute.")
        response = self.api_client._get(url, data=params)
        data = self.api_client._make_api_object(response, type(self))
        self.update(data)
        return data

    def __getattr__(self, *args, **kwargs):
        try:
            return dict.__getitem__(self, *args, **kwargs)
        except KeyError as key_error:
            attribute_error = AttributeError(*key_error.args)
            attribute_error.message = getattr(key_error, "message", "")
            raise attribute_error

    def __delattr__(self, *args, **kwargs):
        try:
            return dict.__delitem__(self, *args, **kwargs)
        except KeyError as key_error:
            attribute_error = AttributeError(*key_error.args)
            attribute_error.message = getattr(key_error, "message", "")
            raise attribute_error

    def __setattr__(self, key, value):
        if key.startswith("_") or key in self.__dict__:
            return dict.__setattr__(self, key, value)
        return dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        data = getattr(self, "data", None)
        if isinstance(data, list) and isinstance(key, (int, slice)):
            return data[key]
        return dict.__getitem__(self, key)

    def __dir__(self):
        return list(self.keys())

    def __str__(self):
        try:
            return json.dumps(self, sort_keys=True, indent=2)
        except TypeError:
            return "(invalid JSON)"

    def __name__(self):
        return "<{} @ {}>".format(type(self).__name__, hex(id(self)))

    def __repr__(self):
        return "{} {}".format(self.__name__(), str(self))


class Campaigns(APIObject):
    def list_all_campaigns(self, scope_ids, **params):
        data = self.api_client.list_campaigns(self.id, scope_ids, **params)
        self.update(data)
        return data


class User(APIObject):
    pass


class CurrentUser(User):
    def get(self):
        """https://percolate.com/docs/api/#/method.api.v5.me"""
        data = self.api_client.get_current_user()
        self.update(data)
        return data

    def get_user_scope_ids(self):
        raise NotImplementedError


_resource_to_model = {
    "campaigns": Campaigns, 
    "user": CurrentUser
}


def new_api_object(client, obj, cls=None, **kwargs):
    if isinstance(obj, dict):
        if not cls:
            resource = obj.get("resource", None)
            cls = _resource_to_model.get(resource, None)
        cls = cls or APIObject
        result = cls(client, **kwargs)
        for k, v in six.iteritems(obj):
            result[k] = new_api_object(client, v)
        return result
    if isinstance(obj, list):
        return [new_api_object(client, v, cls) for v in obj]
    return obj
