# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Auth Class."""
import uuid
from json import dumps as json_dumps

from oauthlib.oauth2 import LegacyApplicationClient, TokenExpiredError
from requests.adapters import HTTPAdapter, Retry
from requests_oauthlib import OAuth2Session

from ring_doorbell.const import API_URI, NAMESPACE_UUID, TIMEOUT, OAuth


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
            # Generate a UUID that will stay the same
            # for this physical device to prevent
            # multiple auth entries in ring.com
            self.hardware_id = str(
                uuid.uuid5(uuid.UUID(NAMESPACE_UUID), str(uuid.getnode()) + user_agent)
            )

        self.device_model = "ring-doorbell"
        self.token_updater = token_updater
        self._oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=OAuth.CLIENT_ID), token=token
        )
        retries = Retry(connect=5, read=0, backoff_factor=2)

        self._oauth.mount(API_URI, HTTPAdapter(max_retries=retries))

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

    def get_device_model(self):
        """Get device model."""
        return self.device_model

    def query(
        self,
        url,
        method="GET",
        extra_params=None,
        data=None,
        json=None,
        timeout=None,
        raise_for_status=True,
    ):
        """Query data from Ring API."""
        if timeout is None:
            timeout = TIMEOUT

        params = {}

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
                kwargs["headers"]["Content-Type"] = "application/json"
            if data is not None:
                kwargs["data"] = data

        if method == "PATCH":
            # PATCH method of requests library does not have a json argument
            if json is not None:
                kwargs["data"] = json_dumps(json)
                kwargs["headers"]["Content-Type"] = "application/json"
            if data is not None:
                kwargs["data"] = data

        try:
            req = getattr(self._oauth, method.lower())(url, **kwargs)
        except TokenExpiredError:
            self._oauth.token = self.refresh_tokens()
            req = getattr(self._oauth, method.lower())(url, **kwargs)

        if raise_for_status:
            req.raise_for_status()

        return req
