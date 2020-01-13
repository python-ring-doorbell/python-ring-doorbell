# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring RingGeneric wrapper."""
import logging

_LOGGER = logging.getLogger(__name__)


# pylint: disable=useless-object-inheritance
class RingGeneric(object):
    """Generic Implementation for Ring Chime/Doorbell."""

    def __init__(self, ring, device_id):
        """Initialize Ring Generic."""
        self._ring = ring
        self.device_id = device_id
        self.capability = False
        self.alert = None

        # alerts notifications
        self.alert_expires_at = None

    def __repr__(self):
        """Return __repr__."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    @property
    def _attrs(self):
        """Return attributes."""
        return self._ring.devices_data[self.family][self.device_id]

    @property
    def name(self):
        """Return name."""
        return self._attrs["description"]

    @property
    def family(self):
        """Return Ring device family type."""
        raise NotImplementedError

    @property
    def model(self):
        """Return Ring device model name."""
        raise NotImplementedError

    def has_capability(self, capability):
        """Return if device has specific capability."""
        return self.capability

    @property
    def account_id(self):
        """Return account ID."""
        return self._ring.account_id

    @property
    def address(self):
        """Return address."""
        return self._attrs.get("address")

    @property
    def firmware(self):
        """Return firmware."""
        return self._attrs.get("firmware_version")

    @property
    def latitude(self):
        """Return latitude attr."""
        return self._attrs.get("latitude")

    @property
    def longitude(self):
        """Return longitude attr."""
        return self._attrs.get("longitude")

    @property
    def kind(self):
        """Return kind attr."""
        return self._attrs.get("kind")

    @property
    def timezone(self):
        """Return timezone."""
        return self._attrs.get("time_zone")

    @property
    def wifi_name(self):
        """Return wifi ESSID name."""
        return self._health_attrs.get("wifi_name")

    @property
    def wifi_signal_strength(self):
        """Return wifi RSSI."""
        return self._health_attrs.get("latest_signal_strength")

    @property
    def wifi_signal_category(self):
        """Return wifi signal category."""
        return self._health_attrs.get("latest_signal_category")
