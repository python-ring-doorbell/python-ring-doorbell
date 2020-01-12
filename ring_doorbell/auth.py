# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Auth Class."""
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import (
    LegacyApplicationClient, TokenExpiredError)
from ring_doorbell.const import OAuth, API_VERSION, TIMEOUT


class Auth:
    """A Python Auth class for Ring"""
    def __init__(self, token=None, token_updater=None):
        """
        :type token: Optional[Dict[str, str]]
        :type token_updater: Optional[Callable[[str], None]]
        """
        self.params = {'api_version': API_VERSION}

        self.token_updater = token_updater
        self._oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=OAuth.CLIENT_ID),
            token=token
        )

    def fetch_token(self, username, password, otp_code=None):
        """Initial token fetch with username/password & 2FA
        :type username: str
        :type password: str
        :type otp_code: str
        """
        if otp_code:
            headers = OAuth.HEADERS.copy()
            headers['2fa-support'] = 'true'
            headers['2fa-code'] = otp_code
        else:
            headers = OAuth.HEADERS

        token = self._oauth.fetch_token(
            OAuth.ENDPOINT,
            username=username,
            password=password,
            scope=OAuth.SCOPE,
            headers=headers
        )

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def refresh_tokens(self):
        """Refreshes the auth tokens"""
        token = self._oauth.refresh_token(
            OAuth.ENDPOINT, headers=OAuth.HEADERS
        )

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def query(self,
              url,
              method='GET',
              extra_params=None,
              json=None,
              timeout=None):
        """Query data from Ring API."""
        if timeout is None:
            timeout = TIMEOUT

        # allow to override params when necessary
        # and update self.params globally for the next connection
        if extra_params:
            params = self.params.copy()
            params.update(extra_params)
        else:
            params = self.params

        kwargs = {
            'params': params,
            'headers': OAuth.HEADERS,
            'timeout': timeout,
        }

        if method == 'POST':
            kwargs['json'] = json

        try:
            req = getattr(self._oauth, method.lower())(url, **kwargs)
        except TokenExpiredError:
            self._oauth.token = self.refresh_tokens()
            req = getattr(self._oauth, method.lower())(url, **kwargs)

        req.raise_for_status()

        return req
