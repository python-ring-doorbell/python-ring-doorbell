# vim:sw=4:ts=4:et:
"""Python Ring RingGeneric wrapper."""


# pylint: disable=useless-object-inheritance
class RingGeneric:
    """Generic Implementation for Ring Chime/Doorbell."""

    # pylint: disable=redefined-builtin
    # pylint:disable=invalid-name
    def __init__(self, ring, device_api_id):
        """Initialize Ring Generic."""
        self._ring = ring
        # This is the account ID of the device.
        # Not the same as device ID.
        self.device_api_id = device_api_id
        self.capability = False
        self.alert = None
        self._health_attrs = {}

        # alerts notifications
        self.alert_expires_at = None

    def __repr__(self):
        """Return __repr__."""
        return f"<{self.__class__.__name__}: {self.name}>"

    def __str__(self):
        return f"{self.name} ({self.kind})"

    def update(self):
        """Update this device info."""
        self.update_health_data()

    def update_health_data(self):
        """Update the health data."""
        raise NotImplementedError

    @property
    def _attrs(self):
        """Return attributes."""
        return self._ring.devices_data[self.family][self.device_api_id]

    @property
    def id(self):
        """Return ID."""
        return self.device_api_id

    @property
    def name(self):
        """Return name."""
        return self._attrs["description"]

    @property
    def device_id(self):
        """Return device ID.

        This is the device_id returned by the api, usually the MAC.
        Not to be confused with the id for the device
        """
        return self._attrs["device_id"]

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
        """Return wifi ESSID name.

        Requires health data to be updated.
        """
        return self._health_attrs.get("wifi_name")

    @property
    def wifi_signal_strength(self):
        """Return wifi RSSI.

        Requires health data to be updated.
        """
        return self._health_attrs.get("latest_signal_strength")

    @property
    def wifi_signal_category(self):
        """Return wifi signal category.

        Requires health data to be updated.
        """
        return self._health_attrs.get("latest_signal_category")
