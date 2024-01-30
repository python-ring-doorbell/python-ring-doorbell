# vim:sw=4:ts=4:et:
"""Python Ring Other (Intercom) wrapper."""
import json
import logging
import uuid

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
)
from ring_doorbell.generic import RingGeneric

_LOGGER = logging.getLogger(__name__)


class RingOther(RingGeneric):
    """Implementation for Ring Intercom."""

    def __init__(self, ring, device_api_id, shared=False):
        super().__init__(ring, device_api_id)
        self.shared = shared

    @property
    def family(self):
        """Return Ring device family type."""
        return "other"

    def update_health_data(self):
        """Update health attrs."""
        self._health_attrs = (
            self._ring.query(HEALTH_DOORBELL_ENDPOINT.format(self.device_api_id))
            .json()
            .get("device_health", {})
        )

    @property
    def model(self):
        """Return Ring device model name."""
        if self.kind in INTERCOM_KINDS:
            return "Intercom"
        return None

    def has_capability(self, capability):
        """Return if device has specific capability."""
        if capability == "open":
            return self.kind in INTERCOM_KINDS
        return False

    @property
    def battery_life(self):
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
    def subscribed(self):
        """Return if is online."""
        if self.kind in INTERCOM_KINDS:
            result = self._attrs.get("subscribed")
            if result is None:
                return False
            return True
        return None

    @property
    def has_subscription(self):
        """Return boolean if the account has subscription."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("features").get("show_recordings")
        return None

    @property
    def unlock_duration(self):
        """Return time unlock switch is held closed"""
        json.loads(
            self._attrs.get("settings").get("intercom_settings").get("config")
        ).get("analog", {}).get("unlock_duration")

    @property
    def doorbell_volume(self):
        """Return doorbell volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("settings").get("doorbell_volume")
        return None

    @doorbell_volume.setter
    def doorbell_volume(self, value):
        if not (
            (isinstance(value, int))
            and (OTHER_DOORBELL_VOL_MIN <= value <= OTHER_DOORBELL_VOL_MAX)
        ):
            _LOGGER.error(
                "%s",
                MSG_VOL_OUTBOUND.format(OTHER_DOORBELL_VOL_MIN, OTHER_DOORBELL_VOL_MAX),
            )
            return False

        params = {
            "doorbot[settings][doorbell_volume]": str(value),
        }
        url = DOORBELLS_ENDPOINT.format(self.device_api_id)
        self._ring.query(url, extra_params=params, method="PUT")
        self._ring.update_devices()
        return True

    @property
    def keep_alive_auto(self):
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("settings").get("keep_alive_auto")
        return None

    @keep_alive_auto.setter
    def keep_alive_auto(self, value):
        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"keep_alive_settings": {"keep_alive_auto": value}}

        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()
        return True

    @property
    def mic_volume(self):
        """Return mic volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("settings").get("mic_volume")
        return None

    @mic_volume.setter
    def mic_volume(self, value):
        if not ((isinstance(value, int)) and (MIC_VOL_MIN <= value <= MIC_VOL_MAX)):
            _LOGGER.error("%s", MSG_VOL_OUTBOUND.format(MIC_VOL_MIN, MIC_VOL_MAX))
            return False

        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"volume_settings": {"mic_volume": value}}

        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()
        return True

    @property
    def voice_volume(self):
        """Return voice volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("settings").get("voice_volume")
        return None

    @voice_volume.setter
    def voice_volume(self, value):
        if not ((isinstance(value, int)) and (VOICE_VOL_MIN <= value <= VOICE_VOL_MAX)):
            _LOGGER.error("%s", MSG_VOL_OUTBOUND.format(VOICE_VOL_MIN, VOICE_VOL_MAX))
            return False

        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"volume_settings": {"voice_volume": value}}

        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()
        return True

    @property
    def clip_length_max(self):
        # this value sets an effective refractory period on consecutive rigns
        # eg if set to default value of 60, rings occuring with 60 seconds of
        # first will not be detected

        url = SETTINGS_ENDPOINT.format(self.device_api_id)

        return (
            self._ring.query(url, method="GET")
            .json()
            .get("video_settings")
            .get("clip_length_max")
        )

    @clip_length_max.setter
    def clip_length_max(self, value):
        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"video_settings": {"clip_length_max": value}}
        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()
        return True

    @property
    def connection_status(self):
        """Return connection status."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("alerts").get("connection")
        return None

    @property
    def location_id(self):
        """Return location id."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("location_id", None)
        return None

    @property
    def allowed_users(self):
        """Return list of users allowed or invited to access"""
        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_ALLOWED_USERS.format(self.location_id)
            return self._ring.query(url, method="GET").json()

        return None

    def open_door(self, user_id=-1):
        """Open the door"""
        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_OPEN_ENDPOINT.format(self.device_api_id)
            request_id = str(uuid.uuid4())
            # request_timestamp = int(time.time() * 1000)
            payload = {
                "command_name": "device_rpc",
                "request": {
                    "id": request_id,
                    "jsonrpc": "2.0",
                    "method": "unlock_door",
                    "params": {
                        # "command_timeout": 5,
                        "door_id": 0,
                        # "issue_time": request_timestamp,
                        "user_id": user_id,
                    },
                },
            }

            response = self._ring.query(url, method="PUT", json=payload).json()
            self._ring.update_devices()
            if response.get("result", {}).get("code", -1) == 0:
                return True

        return False

    def invite_access(self, email):
        """Invite user"""
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

    def remove_access(self, user_id):
        """Remove user access or invitation"""
        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_INVITATIONS_DELETE_ENDPOINT.format(self.location_id, user_id)
            self._ring.query(url, method="DELETE")
            return True

        return False
