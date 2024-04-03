# vim:sw=4:ts=4:et:
"""Python Ring Auth Class."""

from __future__ import annotations

import uuid
from typing import Any, Callable

from oauthlib.oauth2 import (
    LegacyApplicationClient,
    MissingTokenError,
    OAuth2Error,
    TokenExpiredError,
)
from requests import HTTPError, Response, Timeout
from requests.adapters import HTTPAdapter, Retry
from requests_oauthlib import OAuth2Session

from ring_doorbell.const import API_URI, NAMESPACE_UUID, TIMEOUT, OAuth
from ring_doorbell.exceptions import (
    AuthenticationError,
    Requires2FAError,
    RingError,
    RingTimeout,
)


class Auth:
    """A Python Auth class for Ring."""

    def __init__(
        self,
        user_agent: str,
        token: dict[str, Any] | None = None,
        token_updater: Callable[[dict[str, Any]], None] | None = None,
        hardware_id: str | None = None,
    ) -> None:
        """Initialise the auth class.

        :type token: Optional[Dict[str, str]]
        :type token_updater: Optional[Callable[[str], None]]
        """
        self.user_agent = user_agent

        if hardware_id:
            self.hardware_id = hardware_id
        else:
            # Generate a UUID that will stay the same
            # for this physical device to prevent
            # multiple auth entries in ring.com
            self.hardware_id = str(
                uuid.uuid5(uuid.UUID(NAMESPACE_UUID), str(uuid.getnode()) + user_agent)
            )

        self.device_model = "ring-doorbell:" + user_agent
        self.token_updater = token_updater
        self._oauth = OAuth2Session(
            client=LegacyApplicationClient(client_id=OAuth.CLIENT_ID), token=token
        )
        retries = Retry(connect=5, read=0, backoff_factor=2)

        self._oauth.mount(API_URI, HTTPAdapter(max_retries=retries))

    def fetch_token(
        self, username: str, password: str, otp_code: str | None = None
    ) -> dict[str, Any]:
        """Fetch initial token with username/password & 2FA.

        :type username: str
        :type password: str
        :type otp_code: str.
        """
        headers = {"User-Agent": self.user_agent, "hardware_id": self.hardware_id}

        if otp_code:
            headers["2fa-support"] = "true"
            headers["2fa-code"] = otp_code

        try:
            token = self._oauth.fetch_token(
                OAuth.ENDPOINT,
                username=username,
                password=password,
                scope=OAuth.SCOPE,
                headers=headers,
            )
        except MissingTokenError as ex:
            raise Requires2FAError from ex
        except OAuth2Error as ex:
            raise AuthenticationError(ex) from ex

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def refresh_tokens(self) -> dict[str, Any]:
        """Refresh the auth tokens."""
        try:
            token = self._oauth.refresh_token(
                OAuth.ENDPOINT, headers={"User-Agent": self.user_agent}
            )
        except OAuth2Error as ex:
            raise AuthenticationError(ex) from ex

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def get_hardware_id(self) -> str:
        """Get hardware ID."""
        return self.hardware_id

    def get_device_model(self) -> str:
        """Get device model."""
        return self.device_model

    def query(  # noqa: C901, PLR0913, PLR0912
        self,
        url: str,
        method: str = "GET",
        extra_params: dict[str, Any] | None = None,
        data: bytes | None = None,
        json: dict[Any, Any] | None = None,
        timeout: float | None = None,
        *,
        raise_for_status: bool = True,
    ) -> Response:
        """Query data from Ring API."""
        if timeout is None:
            timeout = TIMEOUT

        params = {}

        if extra_params:
            params.update(extra_params)

        kwargs: dict[str, Any] = {
            "params": params,
            "headers": {"User-Agent": self.user_agent},
            "timeout": timeout,
        }

        if json is not None:
            kwargs["json"] = json
            kwargs["headers"]["Content-Type"] = "application/json"  # type: ignore[index]
        if data is not None:
            kwargs["data"] = data

        try:
            try:
                resp = self._oauth.request(method, url, **kwargs)
            except TokenExpiredError:
                self._oauth.token = self.refresh_tokens()
                resp = self._oauth.request(method, url, **kwargs)
        except AuthenticationError:
            raise  # refresh_tokens will return this error if not valid
        except Timeout as ex:
            msg = f"Timeout error during query of url {url}: {ex}"
            raise RingTimeout(msg) from ex
        except Exception as ex:  # noqa: BLE001
            msg = f"Unknown error during query of url {url}: {ex}"
            raise RingError(msg) from ex

        if resp.status_code == 401:
            # Check whether there's an issue with the token grant
            self._oauth.token = self.refresh_tokens()

        if raise_for_status:
            try:
                resp.raise_for_status()
            except HTTPError as ex:
                msg = (
                    f"HTTP error with status code {resp.status_code} "
                    f"during query of url {url}: {ex}"
                )
                raise RingError(msg) from ex

        return resp
