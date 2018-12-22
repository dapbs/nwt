#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import hashlib
import random
import requests
from requests.utils import to_native_string
from requests.auth import AuthBase
import time

from nwt.utils import quote
from nwt.error import build_api_error

import collections

AccessToken = collections.namedtuple("AccessToken", ["access_token", "expires_in"])


class OAuth2Auth(AuthBase):
    def __init__(self, access_token_getter):
        self.access_token_getter = access_token_getter

    def __call__(self, request):
        access_token = self.access_token_getter()
        request.headers.update(
            {
                to_native_string("Authorization"): to_native_string(
                    "Bearer {}".format(access_token)
                )
            }
        )
        return request


class PercolateAuthentication(object):
    """
    Implements a standard OAuth 2.0 flow that involves redirection for users to
    authorize the application to access account data.
    """

    AUTHORIZATION_URL = "https://percolate.com/auth/oauth2/authorization"
    ACCESS_TOKEN_URL = "https://percolate.com/auth/oauth2/accessToken"

    def __init__(self, key, secret, redirect_uri, permissions=None):
        self.key = key
        self.secret = secret
        self.redirect_uri = redirect_uri
        self.permissions = permissions or []
        self.state = None
        self.authorization_code = None
        self.token = None
        self._error = None

    @property
    def authorization_url(self):
        qd = {
            "response_type": "code",
            "client_id": self.key,
            "scope": (" ".join(self.permissions)).strip(),
            "state": self.state or self._make_new_state(),
            "redirect_uri": self.redirect_uri,
        }
        # urlencode uses quote_plus when encoding the query string so,
        # we ought to be encoding the qs by on our own.
        qsl = ["%s=%s" % (quote(k), quote(v)) for k, v in qd.items()]
        return "%s?%s" % (self.AUTHORIZATION_URL, "&".join(qsl))

    @property
    def last_error(self):
        return self._error

    def _make_new_state(self):
        return hashlib.md5(
            "{}{}".format(random.randrange(0, 2 ** 63), self.secret).encode("utf8")
        ).hexdigest()

    def get_access_token(self, timeout=60):
        assert self.authorization_code, "You must first get the authorization code"
        qd = {
            "grant_type": "authorization_code",
            "code": self.authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.key,
            "client_secret": self.secret,
        }
        response = requests.post(self.ACCESS_TOKEN_URL, data=qd, timeout=timeout)
        build_api_error(response)
        response = response.json()
        self.token = AccessToken(response["access_token"], response["expires_in"])
        return self.token
