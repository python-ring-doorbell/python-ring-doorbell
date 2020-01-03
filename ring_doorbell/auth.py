# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Auth Class."""
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import (
    LegacyApplicationClient, TokenExpiredError,
    MissingTokenError)
from ring_doorbell.const import OAuth


class Auth:
    """A Python Auth class for Ring"""
    def __init__(self,
                 token=None,
                 token_updater=None):
        """
        :type token: Optional[Dict[str, str]]
        :type token_updater: Optional[Callable[[str], None]]
        """
        self.token_updater = token_updater
        self._oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=OAuth.CLIENT_ID),
            token=token,
            token_updater=token_updater)

    def fetch_token(self, username, password,
                    auth_callback=None):
        """Initial token fetch with username/password & 2FA
        :type username: str
        :type password: str
        :type auth_callback: Callable[[], str]
        """
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
            headers = {}
            headers['2fa-support'] = 'true'
            headers['2fa-code'] = auth_code

            return self._oauth.fetch_token(
                OAuth.ENDPOINT,
                username=username,
                password=password,
                scope=OAuth.SCOPE,
                headers=headers)

        return self._oauth.fetch_token(
            OAuth.ENDPOINT,
            username=username,
            password=password,
            scope=OAuth.SCOPE)

    # Python 2 doesn't support typing for return value,
    #  removed: -> Dict[str, Union[str, int]]:
    def refresh_tokens(self):
        """Refreshes the auth tokens"""
        token = self._oauth.refresh_token(OAuth.ENDPOINT)

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    # Python 2 doesn't support typing for return value,
    #  removed: -> Response:
    def request(self, method, resource, **kwargs):
        """Does an http request, if token is expired, then it will refresh
        :type method: str
        :type resource: str
        """
        try:
            return self._oauth.request(method, resource, **kwargs)

        except TokenExpiredError:
            self._oauth.token = self.refresh_tokens()
            return self._oauth.request(method, resource, **kwargs)
