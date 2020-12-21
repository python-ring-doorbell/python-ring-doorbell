# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Beam (Transformer) wrapper."""
import logging

from ring_doorbell import RingDoorBell
from ring_doorbell.const import (
    LIGHTS_ENDPOINT,
    MSG_ALLOWED_VALUES,
    HEALTH_DOORBELL_ENDPOINT,
    BEAM_KINDS
)

_LOGGER = logging.getLogger(__name__)


class RingBeam(RingDoorBell):
    """Implementation for RingBeam."""

    @property
    def family(self):
        """Return Ring device family type."""
        return "beams"

    def update_health_data(self):
        """Update health attrs."""
        self._health_attrs = (
            self._ring.query(HEALTH_DOORBELL_ENDPOINT.format(self.id))
            .json()
            .get("device_health", {})
        )

    @property
    def model(self):
        """Return Ring device model name."""
        if self.kind in BEAM_KINDS:
            return "Lighting Transformer"
        return None

    def has_capability(self, capability):
        """Return if device has specific capability."""
        if capability == "light":
            return self.kind in (
                BEAM_KINDS
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

        url = LIGHTS_ENDPOINT.format(self.id, state)
        self._ring.query(url, method="PUT")
        self._ring.update_devices()
        return True
