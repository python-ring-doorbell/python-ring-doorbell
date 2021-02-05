# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring light group wrapper."""
import logging

from ring_doorbell.const import GROUP_DEVICES_ENDPOINT, MSG_ALLOWED_VALUES

_LOGGER = logging.getLogger(__name__)


class RingLightGroup:
    """Implementation for RingLightGroup."""

    # pylint: disable=redefined-builtin
    def __init__(self, ring, id):
        """Initialize Ring Generic."""
        self._ring = ring
        self.id = id  # pylint:disable=invalid-name
        self._health_attrs = {}
        self._health_attrs_fetched = False

    def __repr__(self):
        """Return __repr__."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    def update(self):
        """Update this device info."""
        url = GROUP_DEVICES_ENDPOINT.format(self.location_id, self.id)
        self._health_attrs = self._ring.query(url).json()
        self._health_attrs_fetched = True

    @property
    def _attrs(self):
        """Return attributes."""
        return self._ring.groups_data[self.id]

    @property
    def name(self):
        """Return name."""
        return self._attrs["name"]

    @property
    def family(self):
        """Return Ring device family type."""
        return "group"

    @property
    def device_id(self):
        """Return group ID."""
        # id field holds group ID
        return self.id

    @property
    def location_id(self):
        """Return group location ID."""
        return self._attrs["location_id"]

    @property
    def model(self):
        """Return Ring device model name."""
        return "Light Group"

    # pylint:disable=no-self-use
    def has_capability(self, capability):
        """Return if device has specific capability."""
        if capability == "light":
            return True
        return False

    @property
    def lights(self):
        """Return lights status."""
        if not self._health_attrs_fetched:
            self.update()
        return self._health_attrs["lights_on"]

    @lights.setter
    def lights(self, value):
        """Control the lights."""
        values = ["True", "False"]
        state = None
        duration = None
        if isinstance(value, tuple):
            state, duration = value
        else:
            state = value
        if not isinstance(state, bool):
            _LOGGER.error("%s", MSG_ALLOWED_VALUES.format(", ".join(values)))
            return False

        url = GROUP_DEVICES_ENDPOINT.format(self.location_id, self.id)
        payload = {"lights_on": {"enabled": state}}
        if duration is not None:
            payload["lights_on"]["duration_seconds"] = duration
        self._ring.query(url, method="POST", json=payload)
        self.update()
        return True
