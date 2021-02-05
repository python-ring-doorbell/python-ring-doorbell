# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Auth Class."""
from uuid import uuid4 as uuid
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from ring_doorbell.const import OAuth, API_VERSION, TIMEOUT


class Auth:
    """A Python Auth class for Ring"""

    def __init__(self, user_agent, token=None, token_updater=None, hardware_id=None):
        """
        :type token: Optional[Dict[str, str]]
        :type token_updater: Optional[Callable[[str], None]]
        """
        self.user_agent = user_agent

        self.hardware_id = hardware_id
        if self.hardware_id is None:
            self.hardware_id = str(uuid())

        self.token_updater = token_updater
        self._oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=OAuth.CLIENT_ID), token=token
        )

    def fetch_token(self, username, password, otp_code=None):
        """Initial token fetch with username/password & 2FA
        :type username: str
        :type password: str
        :type otp_code: str
        """
        headers = {"User-Agent": self.user_agent, "hardware_id": self.hardware_id}

        if otp_code:
            headers["2fa-support"] = "true"
            headers["2fa-code"] = otp_code

        token = self._oauth.fetch_token(
            OAuth.ENDPOINT,
            username=username,
            password=password,
            scope=OAuth.SCOPE,
            headers=headers,
        )

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def refresh_tokens(self):
        """Refreshes the auth tokens"""
        token = self._oauth.refresh_token(
            OAuth.ENDPOINT, headers={"User-Agent": self.user_agent}
        )

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def get_hardware_id(self):
        """Get hardware ID."""
        return self.hardware_id

    def query(
        self, url, method="GET", extra_params=None, data=None, json=None, timeout=None
    ):
        """Query data from Ring API."""
        if timeout is None:
            timeout = TIMEOUT

        params = {"api_version": API_VERSION}

        if extra_params:
            params.update(extra_params)

        kwargs = {
            "params": params,
            "headers": {"User-Agent": self.user_agent},
            "timeout": timeout,
        }

        if method == "POST":
            if json is not None:
                kwargs["json"] = json
            if data is not None:
                kwargs["data"] = data

        try:
            req = getattr(self._oauth, method.lower())(url, **kwargs)
        except TokenExpiredError:
            self._oauth.token = self.refresh_tokens()
            req = getattr(self._oauth, method.lower())(url, **kwargs)

        req.raise_for_status()

        return req
