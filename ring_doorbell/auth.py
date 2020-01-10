# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Auth Class."""
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import (
    LegacyApplicationClient, TokenExpiredError,
    MissingTokenError)
from ring_doorbell.const import (OAuth, CACHE_FILE, CACHE_ATTRS,
                                 API_VERSION, TIMEOUT, RETRY_TOKEN)
from ring_doorbell.utils import _exists_cache, _save_cache, _read_cache


class Auth:
    """A Python Auth class for Ring"""
    def __init__(self,
                 token=None,
                 token_updater=None,
                 cache_file=CACHE_FILE):
        """
        :type token: Optional[Dict[str, str]]
        :type token_updater: Optional[Callable[[str], None]]
        """
        self.params = {'api_version': API_VERSION}
        self.cache = CACHE_ATTRS
        self.cache_file = cache_file

        if not token:
            token = self.__load_cache_file()

        self.token_updater = token_updater
        self._oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=OAuth.CLIENT_ID),
            token=token,
            token_updater=token_updater)

    def __default_token_updater(self, token):
        if token:
            self.cache['token'] = token

        _save_cache(self.cache, self.cache_file)

    def __load_cache_file(self):
        """Process cache_file to reuse token instead."""
        if not _exists_cache(self.cache_file):
            return None

        self.cache = _read_cache(self.cache_file)

        return self.cache['token']

    def fetch_token(self, username, password,
                    auth_callback=None):
        """Initial token fetch with username/password & 2FA
        :type username: str
        :type password: str
        :type auth_callback: Callable[[], str]
        """

        token = self.__load_cache_file()

        if token:
            return token

        try:
            return self.__fetch_token(username, password)

        except MissingTokenError:
            if not auth_callback:
                raise

            return self.__fetch_token(username, password, auth_callback())

    def __fetch_token(self, username, password,
                      auth_code=None):
        """Private fetch token method
        :type username: str
        :type password: str
        :type auth_code: str
        """
        if auth_code:
            headers = OAuth.HEADERS.copy()
            headers['2fa-support'] = 'true'
            headers['2fa-code'] = auth_code

            token = self._oauth.fetch_token(
                OAuth.ENDPOINT,
                username=username,
                password=password,
                scope=OAuth.SCOPE,
                headers=headers)

            self.__default_token_updater(token)

            return token

        token = self._oauth.fetch_token(
            OAuth.ENDPOINT,
            username=username,
            password=password,
            scope=OAuth.SCOPE,
            headers=OAuth.HEADERS)

        self.__default_token_updater(token)

        return token

    def refresh_tokens(self):
        """Refreshes the auth tokens"""
        token = self._oauth.refresh_token(
            OAuth.ENDPOINT, headers=OAuth.HEADERS)

        if self.token_updater is not None:
            self.token_updater(token)

        self.__default_token_updater(token)
        return token

    def query(self,
              url,
              attempts=RETRY_TOKEN,
              method='GET',
              raw=False,
              extra_params=None,
              json=None,
              timeout=None):
        """Query data from Ring API."""
        # Configure timeout specific to this query
        query_timeout = timeout or TIMEOUT

        response = None
        loop = 0
        while loop <= attempts:
            # allow to override params when necessary
            # and update self.params globally for the next connection
            if extra_params:
                params = self.params
                params.update(extra_params)
            else:
                params = self.params

            loop += 1
            try:
                if method == 'GET':
                    req = self._oauth.get(
                        url, params=urlencode(params),
                        headers=OAuth.HEADERS,
                        timeout=query_timeout)
                elif method == 'PUT':
                    req = self._oauth.put(
                        url, params=urlencode(params),
                        headers=OAuth.HEADERS,
                        timeout=query_timeout)
                elif method == 'POST':
                    req = self._oauth.post(
                        url, params=urlencode(params), json=json,
                        headers=OAuth.HEADERS,
                        timeout=query_timeout)
            except TokenExpiredError:
                self._oauth.token = self.refresh_tokens()
                req = self.query(url, attempts, method, raw,
                                 extra_params, json, timeout)

            if req.status_code == 200 or req.status_code == 204:
                # if raw, return session object otherwise return JSON
                if raw:
                    response = req
                else:
                    if method == 'GET':
                        response = req.json()
                break

        return response
