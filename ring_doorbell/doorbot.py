# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging
import os
import time
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ring_doorbell.const import (
    DEFAULT_VIDEO_DOWNLOAD_TIMEOUT,
    DINGS_ENDPOINT,
    DOORBELL_2_KINDS,
    DOORBELL_3_KINDS,
    DOORBELL_3_PLUS_KINDS,
    DOORBELL_4_KINDS,
    DOORBELL_ELITE_KINDS,
    DOORBELL_EXISTING_TYPE,
    DOORBELL_GEN2_KINDS,
    DOORBELL_KINDS,
    DOORBELL_PRO_2_KINDS,
    DOORBELL_PRO_KINDS,
    DOORBELL_VOL_MAX,
    DOORBELL_VOL_MIN,
    DOORBELL_WIRED_KINDS,
    DOORBELLS_ENDPOINT,
    FILE_EXISTS,
    HEALTH_DOORBELL_ENDPOINT,
    LIVE_STREAMING_ENDPOINT,
    MSG_ALLOWED_VALUES,
    MSG_BOOLEAN_REQUIRED,
    MSG_EXISTING_TYPE,
    MSG_EXPECTED_ATTRIBUTE_NOT_FOUND,
    MSG_VOL_OUTBOUND,
    PEEPHOLE_CAM_KINDS,
    SETTINGS_ENDPOINT,
    SNAPSHOT_ENDPOINT,
    SNAPSHOT_TIMESTAMP_ENDPOINT,
    URL_RECORDING,
    URL_RECORDING_SHARE_PLAY,
    RingCapability,
)
from ring_doorbell.exceptions import RingError
from ring_doorbell.generic import RingGeneric

_LOGGER = logging.getLogger(__name__)


class RingDoorBell(RingGeneric):
    """Implementation for Ring Doorbell."""

    if TYPE_CHECKING:
        from ring_doorbell.ring import Ring

    def __init__(self, ring: "Ring", device_api_id: int, shared: bool = False) -> None:
        super().__init__(ring, device_api_id)
        self.shared = shared

    @property
    def family(self) -> str:
        """Return Ring device family type."""
        return "authorized_doorbots" if self.shared else "doorbots"

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
        if self.kind in DOORBELL_KINDS:
            return "Doorbell"
        if self.kind in DOORBELL_2_KINDS:
            return "Doorbell 2"
        if self.kind in DOORBELL_3_KINDS:
            return "Doorbell 3"
        if self.kind in DOORBELL_3_PLUS_KINDS:
            return "Doorbell 3 Plus"
        if self.kind in DOORBELL_4_KINDS:
            return "Doorbell 4"
        if self.kind in DOORBELL_PRO_KINDS:
            return "Doorbell Pro"
        if self.kind in DOORBELL_PRO_2_KINDS:
            return "Doorbell Pro 2"
        if self.kind in DOORBELL_ELITE_KINDS:
            return "Doorbell Elite"
        if self.kind in DOORBELL_WIRED_KINDS:
            return "Doorbell Wired"
        if self.kind in DOORBELL_GEN2_KINDS:
            return "Doorbell (2nd Gen)"
        if self.kind in PEEPHOLE_CAM_KINDS:
            return "Peephole Cam"
        return "Unknown Doorbell"

    def has_capability(self, capability: Union[RingCapability, str]) -> bool:
        """Return if device has specific capability."""
        capability = (
            capability
            if isinstance(capability, RingCapability)
            else RingCapability.from_name(capability)
        )
        if capability == RingCapability.BATTERY:
            return self.kind in (
                DOORBELL_KINDS
                + DOORBELL_2_KINDS
                + DOORBELL_3_KINDS
                + DOORBELL_3_PLUS_KINDS
                + DOORBELL_4_KINDS
                + DOORBELL_GEN2_KINDS
                + PEEPHOLE_CAM_KINDS
            )
        if capability == RingCapability.KNOCK:
            return self.kind in PEEPHOLE_CAM_KINDS
        if capability == RingCapability.PRE_ROLL:
            return self.kind in DOORBELL_3_PLUS_KINDS
        if capability == RingCapability.VOLUME:
            return True
        if capability == RingCapability.HISTORY:
            return True
        if capability in [RingCapability.MOTION_DETECTION, RingCapability.VIDEO]:
            return self.kind in (
                DOORBELL_KINDS
                + DOORBELL_2_KINDS
                + DOORBELL_3_KINDS
                + DOORBELL_3_PLUS_KINDS
                + DOORBELL_4_KINDS
                + DOORBELL_PRO_KINDS
                + DOORBELL_PRO_2_KINDS
                + DOORBELL_WIRED_KINDS
                + DOORBELL_GEN2_KINDS
                + PEEPHOLE_CAM_KINDS
            )
        return False

    @property
    def battery_life(self) -> Optional[int]:
        """Return battery life."""
        if (
            bl1 := self._attrs.get("battery_life")
        ) is None and "battery_life_2" not in self._attrs:
            return None

        value = 0
        if bl1:
            value += int(bl1)

        if bl2 := self._attrs.get("battery_life_2"):  # Camera has two battery bays
            value += int(bl2)

        if value > 100:
            value = 100
        return value

    def _get_chime_setting(self, setting: str) -> Optional[Any]:
        if (settings := self._attrs.get("settings")) and (
            chime_settings := settings.get("chime_settings")
        ):
            return chime_settings.get(setting)
        return None

    @property
    def existing_doorbell_type(self) -> Optional[str]:
        """
        Return existing doorbell type.

        0: Mechanical
        1: Digital
        2: Not Present
        """
        try:
            if (dtype := self._get_chime_setting("type")) is not None:
                return DOORBELL_EXISTING_TYPE[dtype]
            return None
        except AttributeError:
            return None

    @existing_doorbell_type.setter
    def existing_doorbell_type(self, value: int) -> None:
        """
        Return existing doorbell type.

        0: Mechanical
        1: Digital
        2: Not Present
        """
        if value not in DOORBELL_EXISTING_TYPE:
            raise RingError(f"value must be in {MSG_EXISTING_TYPE}")
        params = {
            "doorbot[description]": self.name,
            "doorbot[settings][chime_settings][type]": value,
        }
        if self.existing_doorbell_type:
            url = DOORBELLS_ENDPOINT.format(self.device_api_id)
            self._ring.query(url, extra_params=params, method="PUT")
            self._ring.update_devices()

    @property
    def existing_doorbell_type_enabled(self) -> Optional[bool]:
        """Return if existing doorbell type is enabled."""
        if self.existing_doorbell_type:
            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[2]:
                return None
            return self._get_chime_setting("enable")
        return False

    @existing_doorbell_type_enabled.setter
    def existing_doorbell_type_enabled(self, value: bool) -> None:
        """Enable/disable the existing doorbell if Digital/Mechanical."""
        if self.existing_doorbell_type:
            if not isinstance(value, bool):
                raise RingError(MSG_BOOLEAN_REQUIRED)

            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[2]:
                return

            params = {
                "doorbot[description]": self.name,
                "doorbot[settings][chime_settings][enable]": value,
            }
            url = DOORBELLS_ENDPOINT.format(self.device_api_id)
            self._ring.query(url, extra_params=params, method="PUT")
            self._ring.update_devices()

    @property
    def existing_doorbell_type_duration(self) -> Optional[int]:
        """Return duration for Digital chime."""
        if (
            self.existing_doorbell_type
            and self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[1]
        ):
            return self._get_chime_setting("duration")
        return None

    @existing_doorbell_type_duration.setter
    def existing_doorbell_type_duration(self, value: int) -> None:
        """Set duration for Digital chime."""
        if self.existing_doorbell_type:
            if not (
                (isinstance(value, int))
                and (DOORBELL_VOL_MIN <= value <= DOORBELL_VOL_MAX)
            ):
                raise RingError(
                    MSG_VOL_OUTBOUND.format(DOORBELL_VOL_MIN, DOORBELL_VOL_MAX)
                )

            if self.existing_doorbell_type == DOORBELL_EXISTING_TYPE[1]:
                params = {
                    "doorbot[description]": self.name,
                    "doorbot[settings][chime_settings][duration]": value,
                }
                url = DOORBELLS_ENDPOINT.format(self.device_api_id)
                self._ring.query(url, extra_params=params, method="PUT")
                self._ring.update_devices()

    @property
    def last_recording_id(self) -> Optional[int]:
        """Return the last recording ID."""
        try:
            res = self.history(limit=1)
            return res[0].get("id") if res else None
        except (IndexError, TypeError):
            return None

    @property
    def live_streaming_json(self) -> Optional[Dict[str, Any]]:
        """Return JSON for live streaming."""
        url = LIVE_STREAMING_ENDPOINT.format(self.device_api_id)
        req = self._ring.query(url, method="POST")
        if req and req.status_code == 200:
            url = DINGS_ENDPOINT
            try:
                return self._ring.query(url).json()[0]
            except (IndexError, TypeError):
                pass
        return None

    def recording_download(
        self,
        recording_id: int,
        filename: Optional[str] = None,
        override: bool = False,
        timeout: int = DEFAULT_VIDEO_DOWNLOAD_TIMEOUT,
    ) -> Optional[bytes]:
        """Save a recording in MP4 format to a file or return raw."""
        if not self.has_subscription:
            msg = "Your Ring account does not have an active subscription."
            _LOGGER.warning(msg)
            return None

        url = URL_RECORDING.format(recording_id)
        try:
            # Video download needs a longer timeout to get the large video file
            req = self._ring.query(url, timeout=timeout)
            if req.status_code == 200:
                if filename:
                    if os.path.isfile(filename) and not override:
                        raise RingError(FILE_EXISTS.format(filename))

                    with open(filename, "wb") as recording:
                        recording.write(req.content)
                        return None
                else:
                    return req.content
            else:
                raise RingError(
                    f"Could not get recording at url {url}, "
                    + f"status code is {req.status_code}"
                )
        except OSError as error:
            msg = f"Error downloading recording {recording_id}: {error}"
            _LOGGER.error(msg)
            raise RingError(msg) from error

    def recording_url(self, recording_id: int) -> Optional[str]:
        """Return HTTPS recording URL."""
        if not self.has_subscription:
            msg = "Your Ring account does not have an active subscription."
            _LOGGER.warning(msg)
            return None

        url = URL_RECORDING_SHARE_PLAY.format(recording_id)
        req = self._ring.query(url)
        data = req.json()
        if req and req.status_code == 200 and data is not None:
            return data["url"]
        return None

    @property
    def subscribed(self) -> bool:
        """Return if is online."""
        result = self._attrs.get("subscribed")
        if result is None:
            return False
        return True

    @property
    def subscribed_motion(self) -> bool:
        """Return if is subscribed_motion."""
        result = self._attrs.get("subscribed_motions")
        if result is None:
            return False
        return True

    @property
    def has_subscription(self) -> bool:
        """Return boolean if the account has subscription."""
        if features := self._attrs.get("features"):
            return features.get("show_recordings", False)
        return False

    @property
    def volume(self) -> int:
        """Return volume."""
        return self._attrs["settings"].get("doorbell_volume", 0)

    @volume.setter
    def volume(self, value: int) -> None:
        if not (
            (isinstance(value, int)) and (DOORBELL_VOL_MIN <= value <= DOORBELL_VOL_MAX)
        ):
            raise RingError(MSG_VOL_OUTBOUND.format(DOORBELL_VOL_MIN, DOORBELL_VOL_MAX))

        params = {
            "doorbot[description]": self.name,
            "doorbot[settings][doorbell_volume]": str(value),
        }
        url = DOORBELLS_ENDPOINT.format(self.device_api_id)
        self._ring.query(url, extra_params=params, method="PUT")
        self._ring.update_devices()

    @property
    def connection_status(self) -> Optional[str]:
        """Return connection status."""
        if alerts := self._attrs.get("alerts"):
            return alerts.get("connection")
        return None

    def get_snapshot(
        self, retries: int = 3, delay: int = 1, filename: Optional[str] = None
    ) -> Optional[bytes]:
        """Take a snapshot and download it"""
        url = SNAPSHOT_TIMESTAMP_ENDPOINT
        payload = {"doorbot_ids": [self._attrs.get("id")]}
        self._ring.query(url, method="POST", json=payload)
        request_time = time.time()
        for _ in range(retries):
            time.sleep(delay)
            response = self._ring.query(url, method="POST", json=payload).json()
            if response["timestamps"][0]["timestamp"] / 1000 > request_time:
                snapshot = self._ring.query(
                    SNAPSHOT_ENDPOINT.format(self._attrs.get("id"))
                ).content
                if filename:
                    with open(filename, "wb") as jpg:
                        jpg.write(snapshot)
                    return None
                return snapshot
        return None

    def _motion_detection_state(self) -> Optional[bool]:
        if settings := self._attrs.get("settings"):
            return settings.get("motion_detection_enabled")
        return None

    @property
    def motion_detection(self) -> bool:
        """Return motion detection enabled state."""
        return state if (state := self._motion_detection_state()) else False

    @motion_detection.setter
    def motion_detection(self, state: bool) -> None:
        """Set the motion detection enabled state."""
        values = [True, False]
        if state not in values:
            raise RingError(MSG_ALLOWED_VALUES.format("True, False"))

        if self._motion_detection_state() is None:
            _LOGGER.warning(
                "%s",
                MSG_EXPECTED_ATTRIBUTE_NOT_FOUND.format(
                    "settings[motion_detection_enabled]"
                ),
            )
            return None

        url = SETTINGS_ENDPOINT.format(self.device_api_id)
        payload = {"motion_settings": {"motion_detection_enabled": state}}

        self._ring.query(url, method="PATCH", json=payload)
        self._ring.update_devices()
