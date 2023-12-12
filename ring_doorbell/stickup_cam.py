# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Doorbell wrapper."""
import logging

from ring_doorbell.const import (
    FLOODLIGHT_CAM_KINDS,
    FLOODLIGHT_CAM_PLUS_KINDS,
    FLOODLIGHT_CAM_PRO_KINDS,
    HEALTH_DOORBELL_ENDPOINT,
    INDOOR_CAM_GEN2_KINDS,
    INDOOR_CAM_KINDS,
    LIGHTS_ENDPOINT,
    MSG_ALLOWED_VALUES,
    MSG_VOL_OUTBOUND,
    SIREN_DURATION_MAX,
    SIREN_DURATION_MIN,
    SIREN_ENDPOINT,
    SPOTLIGHT_CAM_BATTERY_KINDS,
    SPOTLIGHT_CAM_PLUS_KINDS,
    SPOTLIGHT_CAM_PRO_KINDS,
    SPOTLIGHT_CAM_WIRED_KINDS,
    STICKUP_CAM_BATTERY_KINDS,
    STICKUP_CAM_ELITE_KINDS,
    STICKUP_CAM_GEN3_KINDS,
    STICKUP_CAM_KINDS,
)
from ring_doorbell.doorbot import RingDoorBell

_LOGGER = logging.getLogger(__name__)


class RingStickUpCam(RingDoorBell):
    """Implementation for RingStickUpCam."""

    @property
    def family(self):
        """Return Ring device family type."""
        return "stickup_cams"

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
        if self.kind in FLOODLIGHT_CAM_KINDS:
            return "Floodlight Cam"
        if self.kind in FLOODLIGHT_CAM_PRO_KINDS:
            return "Floodlight Cam Pro"
        if self.kind in FLOODLIGHT_CAM_PLUS_KINDS:
            return "Floodlight Cam Plus"
        if self.kind in INDOOR_CAM_KINDS:
            return "Indoor Cam"
        if self.kind in INDOOR_CAM_GEN2_KINDS:
            return "Indoor Cam (2nd Gen)"
        if self.kind in SPOTLIGHT_CAM_BATTERY_KINDS:
            return "Spotlight Cam {}".format(
                self._attrs.get("ring_cam_setup_flow", "battery").title()
            )
        if self.kind in SPOTLIGHT_CAM_WIRED_KINDS:
            return "Spotlight Cam {}".format(
                self._attrs.get("ring_cam_setup_flow", "wired").title()
            )
        if self.kind in SPOTLIGHT_CAM_PLUS_KINDS:
            return "Spotlight Cam Plus"
        if self.kind in SPOTLIGHT_CAM_PRO_KINDS:
            return "Spotlight Cam Pro"
        if self.kind in STICKUP_CAM_KINDS:
            return "Stick Up Cam"
        if self.kind in STICKUP_CAM_BATTERY_KINDS:
            return "Stick Up Cam Battery"
        if self.kind in STICKUP_CAM_ELITE_KINDS:
            return "Stick Up Cam Wired"
        if self.kind in STICKUP_CAM_GEN3_KINDS:
            return "Stick Up Cam (3rd Gen)"
        _LOGGER.error("Unknown kind: %s", self.kind)
        return None

    def has_capability(self, capability):
        """Return if device has specific capability."""
        if capability == "battery":
            return self.kind in (
                SPOTLIGHT_CAM_BATTERY_KINDS
                + STICKUP_CAM_KINDS
                + STICKUP_CAM_BATTERY_KINDS
                + STICKUP_CAM_GEN3_KINDS
            )
        if capability == "light":
            return self.kind in (
                FLOODLIGHT_CAM_KINDS
                + FLOODLIGHT_CAM_PRO_KINDS
                + FLOODLIGHT_CAM_PLUS_KINDS
                + SPOTLIGHT_CAM_BATTERY_KINDS
                + SPOTLIGHT_CAM_WIRED_KINDS
                + SPOTLIGHT_CAM_PLUS_KINDS
                + SPOTLIGHT_CAM_PRO_KINDS
            )
        if capability == "siren":
            return self.kind in (
                FLOODLIGHT_CAM_KINDS
                + FLOODLIGHT_CAM_PRO_KINDS
                + FLOODLIGHT_CAM_PLUS_KINDS
                + INDOOR_CAM_KINDS
                + INDOOR_CAM_GEN2_KINDS
                + SPOTLIGHT_CAM_BATTERY_KINDS
                + SPOTLIGHT_CAM_WIRED_KINDS
                + SPOTLIGHT_CAM_PLUS_KINDS
                + SPOTLIGHT_CAM_PRO_KINDS
                + STICKUP_CAM_BATTERY_KINDS
                + STICKUP_CAM_ELITE_KINDS
                + STICKUP_CAM_GEN3_KINDS
            )
        if capability in ("motion_detection", "video"):
            return self.kind in (
                FLOODLIGHT_CAM_KINDS
                + FLOODLIGHT_CAM_PRO_KINDS
                + FLOODLIGHT_CAM_PLUS_KINDS
                + INDOOR_CAM_KINDS
                + INDOOR_CAM_GEN2_KINDS
                + SPOTLIGHT_CAM_BATTERY_KINDS
                + SPOTLIGHT_CAM_WIRED_KINDS
                + SPOTLIGHT_CAM_PLUS_KINDS
                + SPOTLIGHT_CAM_PRO_KINDS
                + STICKUP_CAM_KINDS
                + STICKUP_CAM_BATTERY_KINDS
                + STICKUP_CAM_ELITE_KINDS
                + STICKUP_CAM_GEN3_KINDS
            )
        return False

    @property
    def lights(self):
        """Return lights status."""
        return self._attrs.get("led_status")

    @lights.setter
    def lights(self, state):
        """Control the lights."""
        values = ["on", "off"]
        if state not in values:
            _LOGGER.error("%s", MSG_ALLOWED_VALUES.format(", ".join(values)))
            return False

        url = LIGHTS_ENDPOINT.format(self.device_api_id, state)
        self._ring.query(url, method="PUT")
        self._ring.update_devices()
        return True

    @property
    def siren(self):
        """Return siren status."""
        if self._attrs.get("siren_status"):
            return self._attrs.get("siren_status").get("seconds_remaining")
        return None

    @siren.setter
    def siren(self, duration):
        """Control the siren."""
        if not (
            (isinstance(duration, int))
            and (SIREN_DURATION_MIN <= duration <= SIREN_DURATION_MAX)
        ):
            _LOGGER.error(
                "%s", MSG_VOL_OUTBOUND.format(SIREN_DURATION_MIN, SIREN_DURATION_MAX)
            )
            return False

        if duration > 0:
            state = "on"
            params = {"duration": duration}
        else:
            state = "off"
            params = {}
        url = SIREN_ENDPOINT.format(self.device_api_id, state)
        self._ring.query(url, extra_params=params, method="PUT")
        self._ring.update_devices()
        return True
