# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring RingGeneric wrapper."""
import logging
from datetime import datetime

from ring_doorbell.utils import _locator
from ring_doorbell.const import (
    API_URI, DEVICES_ENDPOINT, NOT_FOUND,
    HEALTH_CHIMES_ENDPOINT, HEALTH_DOORBELL_ENDPOINT)

_LOGGER = logging.getLogger(__name__)


# pylint: disable=useless-object-inheritance
class RingGeneric(object):
    """Generic Implementation for Ring Chime/Doorbell."""

    def __init__(self, ring, attrs, shared=False):
        """Initialize Ring Generic."""
        self._ring = ring
        self.shared = shared
        self._attrs = attrs
        self._health_attrs = None
        self.capability = False
        self.alert = None

        # alerts notifications
        self.alert_expires_at = None

    def __repr__(self):
        """Return __repr__."""
        return "<{0}: {1}>".format(self.__class__.__name__, self.name)

    @property
    def name(self):
        """Return name."""
        return self._attrs['description']

    @property
    def family(self):
        """Return Ring device family type."""
        return None

    @property
    def model(self):
        """Return Ring device model name."""
        return None

    def has_capability(self, capability):
        """Return if device has specific capability."""
        return self.capability

    def update(self):
        """Refresh attributes."""
        self._get_attrs()
        self._get_health_attrs()
        self._update_alert()

    def _update_alert(self):
        """Verify if alert received is still valid."""
        # alert is no longer valid
        if self.alert and self.alert_expires_at:
            if datetime.now() >= self.alert_expires_at:
                self.alert = None
                self.alert_expires_at = None

    def _get_attrs(self):
        """Return attributes."""
        url = API_URI + DEVICES_ENDPOINT
        if self.family == 'doorbots' and self.shared:
            lst = self._ring.query(url).json().get('authorized_doorbots')
        else:
            lst = self._ring.query(url).json().get(self.family)
        index = _locator(lst, 'description', self.name)
        if index == NOT_FOUND:
            return None

        self._attrs = lst[index]
        return True

    def _get_health_attrs(self):
        """Return health attributes."""
        if self.family == 'doorbots' or self.family == 'stickup_cams':
            url = API_URI + HEALTH_DOORBELL_ENDPOINT.format(self.account_id)
        elif self.family == 'chimes':
            url = API_URI + HEALTH_CHIMES_ENDPOINT.format(self.account_id)
        self._health_attrs = self._ring.query(url).json().get('device_health')

    @property
    def account_id(self):
        """Return account ID."""
        return self._attrs.get('id')

    @property
    def address(self):
        """Return address."""
        return self._attrs.get('address')

    @property
    def firmware(self):
        """Return firmware."""
        return self._attrs.get('firmware_version')

    # pylint: disable=invalid-name
    @property
    def id(self):
        """Return ID."""
        return self._attrs.get('device_id')

    @property
    def latitude(self):
        """Return latitude attr."""
        return self._attrs.get('latitude')

    @property
    def longitude(self):
        """Return longitude attr."""
        return self._attrs.get('longitude')

    @property
    def kind(self):
        """Return kind attr."""
        return self._attrs.get('kind')

    @property
    def timezone(self):
        """Return timezone."""
        return self._attrs.get('time_zone')

    @property
    def wifi_name(self):
        """Return wifi ESSID name."""
        return self._health_attrs.get('wifi_name')

    @property
    def wifi_signal_strength(self):
        """Return wifi RSSI."""
        return self._health_attrs.get('latest_signal_strength')

    @property
    def wifi_signal_category(self):
        """Return wifi signal category."""
        return self._health_attrs.get('latest_signal_category')
