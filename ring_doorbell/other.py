# vim:sw=4:ts=4:et:
"""Python Ring Other (Intercom) wrapper."""

from __future__ import annotations

import json
import logging
import uuid
from typing import TYPE_CHECKING, Any

from ring_doorbell.const import (
    DOORBELLS_ENDPOINT,
    HEALTH_DOORBELL_ENDPOINT,
    INTERCOM_ALLOWED_USERS,
    INTERCOM_INVITATIONS_DELETE_ENDPOINT,
    INTERCOM_INVITATIONS_ENDPOINT,
    INTERCOM_KINDS,
    INTERCOM_OPEN_ENDPOINT,
    MIC_VOL_MAX,
    MIC_VOL_MIN,
    MSG_VOL_OUTBOUND,
    OTHER_DOORBELL_VOL_MAX,
    OTHER_DOORBELL_VOL_MIN,
    SETTINGS_ENDPOINT,
    VOICE_VOL_MAX,
    VOICE_VOL_MIN,
    RingCapability,
)
from ring_doorbell.exceptions import RingError
from ring_doorbell.generic import RingGeneric

_LOGGER = logging.getLogger(__name__)


class RingOther(RingGeneric):
    """Implementation for Ring Intercom."""

    if TYPE_CHECKING:
        from ring_doorbell.ring import Ring

    def __init__(self, ring: Ring, device_api_id: int, *, shared: bool = False) -> None:
        """Initialise the other devices."""
        super().__init__(ring, device_api_id)
        self.shared = shared

    @property
    def family(self) -> str:
        """Return Ring device family type."""
        return "other"

    def update_health_data(self) -> None:
        """Update health attrs."""
        self._health_attrs = (
            self._ring.query(HEALTH_DOORBELL_ENDPOINT.format(self.device_api_id))
            .json()
            .get("device_health", {})
        )

    @property
    def model(self) -> str:
        """Return Ring device model name."""
        if self.kind in INTERCOM_KINDS:
            return "Intercom"
        return "Unknown Other"

    def has_capability(self, capability: RingCapability | str) -> bool:
        """Return if device has specific capability."""
        capability = (
            capability
            if isinstance(capability, RingCapability)
            else RingCapability.from_name(capability)
        )
        if capability in [RingCapability.OPEN, RingCapability.HISTORY]:
            return self.kind in INTERCOM_KINDS
        return False

    @property
    def battery_life(self) -> int | None:
        """Return battery life."""
        if self.kind in INTERCOM_KINDS:
            if self._attrs.get("battery_life") is None:
                return None

            value = int(self._attrs.get("battery_life", 0))
            if value and value > 100:
                value = 100

            return value
        return None

    @property
    def subscribed(self) -> bool:
        """Return if is online."""
        if self.kind in INTERCOM_KINDS:
            result = self._attrs.get("subscribed")
            if result is None:
                return False
            return True
        return False

    @property
    def has_subscription(self) -> bool:
        """Return boolean if the account has subscription."""
        if self.kind in INTERCOM_KINDS and (features := self._attrs.get("features")):
            return features.get("show_recordings", False)
        return False

    @property
    def unlock_duration(self) -> str | None:
        """Return time unlock switch is held closed."""
        return (
            json.loads(self._attrs["settings"]["intercom_settings"]["config"])
            .get("analog", {})
            .get("unlock_duration")
        )

    @property
    def doorbell_volume(self) -> int:
        """Return doorbell volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs["settings"].get("doorbell_volume", 0)
        return 0

    @doorbell_volume.setter
    def doorbell_volume(self, value: int) -> None:
        if not (
            (isinstance(value, int))
            and (OTHER_DOORBELL_VOL_MIN <= value <= OTHER_DOORBELL_VOL_MAX)
        ):
            raise RingError(
                MSG_VOL_OUTBOUND.format(OTHER_DOORBELL_VOL_MIN, OTHER_DOORBELL_VOL_MAX)
            )

        params = {
            "doorbot[settings][doorbell_volume]": str(value),
        }
        url = DOORBELLS_ENDPOINT.format(self.device_api_id)
        self._ring.query(url, extra_params=params, method="PUT")
        self._ring.update_devices()

    @property
    def keep_alive_auto(self) -> float | None:
        """The keep alive auto setting."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs["settings"].get("keep_alive_auto")
        return None

    @keep_alive_auto.setter
    def keep_alive_auto(self, value: float) -> None:
        """Update the keep alive auto setting."""
        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"keep_alive_settings": {"keep_alive_auto": value}}

        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()

    @property
    def mic_volume(self) -> int | None:
        """Return mic volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs["settings"].get("mic_volume")
        return None

    @mic_volume.setter
    def mic_volume(self, value: int) -> None:
        if not ((isinstance(value, int)) and (MIC_VOL_MIN <= value <= MIC_VOL_MAX)):
            raise RingError(MSG_VOL_OUTBOUND.format(MIC_VOL_MIN, MIC_VOL_MAX))

        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"volume_settings": {"mic_volume": value}}

        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()

    @property
    def voice_volume(self) -> int | None:
        """Return voice volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs["settings"].get("voice_volume")
        return None

    @voice_volume.setter
    def voice_volume(self, value: int) -> None:
        if not ((isinstance(value, int)) and (VOICE_VOL_MIN <= value <= VOICE_VOL_MAX)):
            raise RingError(MSG_VOL_OUTBOUND.format(VOICE_VOL_MIN, VOICE_VOL_MAX))

        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"volume_settings": {"voice_volume": value}}

        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()

    @property
    def clip_length_max(self) -> int | None:
        """Maximum clip length.

        This value sets an effective refractory period on consecutive rigns
        eg if set to default value of 60, rings occuring with 60 seconds of
        first will not be detected.
        """
        url = SETTINGS_ENDPOINT.format(self.device_api_id)

        return (
            self._ring.query(url, method="GET")
            .json()
            .get("video_settings", {})
            .get("clip_length_max")
        )

    @clip_length_max.setter
    def clip_length_max(self, value: int) -> None:
        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"video_settings": {"clip_length_max": value}}
        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()

    @property
    def connection_status(self) -> str | None:
        """Return connection status."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("alerts", {}).get("connection")
        return None

    @property
    def allowed_users(self) -> list[dict[str, Any]] | None:
        """Return list of users allowed or invited to access."""
        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_ALLOWED_USERS.format(self.location_id)
            return self._ring.query(url, method="GET").json()

        return None

    def open_door(self, user_id: int = -1) -> bool:
        """Open the door."""
        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_OPEN_ENDPOINT.format(self.device_api_id)
            request_id = str(uuid.uuid4())
            # params can also accept:
            # issue_time: in seconds
            # command_timeout: in seconds
            payload = {
                "command_name": "device_rpc",
                "request": {
                    "id": request_id,
                    "jsonrpc": "2.0",
                    "method": "unlock_door",
                    "params": {
                        "door_id": 0,
                        "user_id": user_id,
                    },
                },
            }

            response = self._ring.query(url, method="PUT", json=payload).json()
            self._ring.update_devices()
            if response.get("result", {}).get("code", -1) == 0:
                return True

        return False

    def invite_access(self, email: str) -> bool:
        """Invite user."""
        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_INVITATIONS_ENDPOINT.format(self.location_id)
            payload = {
                "invitation": {
                    "doorbot_ids": [self.device_api_id],
                    "invited_email": email,
                    "group_ids": [],
                }
            }
            self._ring.query(url, method="POST", json=payload)
            return True

        return False

    def remove_access(self, user_id: int) -> bool:
        """Remove user access or invitation."""
        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_INVITATIONS_DELETE_ENDPOINT.format(self.location_id, user_id)
            self._ring.query(url, method="DELETE")
            return True

        return False
